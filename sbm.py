#!/usr/bin/python

from flask import Flask, jsonify, make_response, request, render_template

from flask_sqlalchemy import SQLAlchemy

import socket
import datetime
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
db.create_all()


class BootConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    config = db.Column(db.Text, unique=True)

    def __init__(self, title, config):
        self.title = title
        self.config = config

    def __repr__(self):
        return '<Config {}>'.format(repr(self.title))


class Machine(db.Model):
    _switch_type = ['switched', 'alternating', 'timed']
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(80), unique=True)
    default_boot_id = db.Column(
        db.Integer,
        db.ForeignKey('boot_config.id')
    )
    default_boot = db.relationship(
        'BootConfig',
        foreign_keys=[default_boot_id]
    )
    alternate_boot_id = db.Column(
        db.Integer,
        db.ForeignKey('boot_config.id')
    )
    alternate_boot = db.relationship(
        'BootConfig',
        foreign_keys=[alternate_boot_id]
    )
    switch_type = db.Column(db.Integer)
    use_alternate = db.Column(db.Boolean)
    last_boot = db.Column(db.DateTime)
    time_between = db.Column(db.Integer)

    def __init__(self, hostname, default_boot,
                 alternate_boot, switch_type='switched'):
        self.hostname = hostname
        self.default_boot = default_boot
        self.alternate_boot = alternate_boot
        self.switch_type = self._switch_type.index(switch_type)
        self.use_alternate = False
        self.last_boot = datetime.datetime(1970, 1, 1)
        self.time_between = 600

    def __repr__(self):
        return '<Machine {} -- {} -- {} -- {}>'.format(
            repr(self.hostname),
            repr(self.default_boot),
            repr(self.alternate_boot),
            repr(self._switch_type[self.switch_type])
        )


def set_machine_definition(mdjson):
    mdjson = {i['name']: i['value'] for i in mdjson}
    md = get_machine_definition(mdjson['hostname'])
    dbc = get_boot_config_definition(mdjson['default_boot'])
    abc = get_boot_config_definition(mdjson['alternate_boot'])
    if md is None:
        md = Machine(mdjson['hostname'], dbc, abc, mdjson['switch_type'])
        db.session.add(md)
    md.alternate_boot = abc
    md.default_boot = dbc
    md.switch_type = md._switch_type.index(mdjson['switch_type'])
    md.time_between = mdjson['time_between']
    db.session.commit()


def get_list_of_machines():
    all_machines = Machine.query.all()
    return [machine.hostname for machine in all_machines]


def get_machine_definition(hostname):
    return Machine.query.filter_by(hostname=hostname).first()


def remove_machine_definition(hostname):
    machine = get_machine_definition(hostname)
    db.session.delete(machine)
    db.session.commit()


def set_boot_config_definition(bcjson):
    bcjson = {i['name']: i['value'] for i in bcjson}
    bc = get_boot_config_definition(bcjson['title'])
    if bc is None:
        bc = BootConfig(bcjson['title'], bcjson['config'])
        db.session.add(bc)
    bc.config = bcjson['config']
    db.session.commit()


def get_list_of_boot_configs():
    all_boot_configs = BootConfig.query.all()
    return [config.title for config in all_boot_configs]


def get_boot_config_definition(title):
    return BootConfig.query.filter_by(title=title).first()


def remove_boot_config_definition(title):
    boot_config = get_boot_config_definition(title)
    db.session.delete(boot_config)
    db.session.commit()


@app.route('/api/v1/machine/', methods=['GET', 'PUT'])
def api_v1_machine():
    if request.method == 'PUT':
        try:
            set_machine_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        machine_list = get_list_of_machines()
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    return jsonify(*machine_list)


@app.route('/api/v1/boot_config/', methods=['GET', 'PUT'])
def api_v1_boot_config():
    if request.method == 'PUT':
        try:
            set_boot_config_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        boot_config_list = get_list_of_boot_configs()
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    return jsonify(*boot_config_list)


@app.route('/api/v1/machine/<hostname>/', methods=['GET', 'POST', 'DELETE'])
def api_v1_machine_hostname(hostname):
    if request.method == 'POST':
        try:
            set_machine_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        machine = get_machine_definition(hostname)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if request.method == 'DELETE':
        try:
            remove_machine_definition(hostname)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
        return jsonify(status="ok")
    fm = {}
    fm['switch_type'] = machine._switch_type[machine.switch_type]
    for item in ['hostname', 'use_alternate', 'last_boot', 'time_between']:
        fm[item] = getattr(machine, item)
    for item in ['default_boot', 'alternate_boot']:
        fm[item] = getattr(machine, item).title
    return jsonify(**fm)


@app.route('/api/v1/boot_config/<title>/', methods=['GET', 'POST', 'DELETE'])
def api_v1_boot_config_title(title):
    if request.method == 'POST':
        try:
            set_boot_config_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        boot_config = get_boot_config_definition(title)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if request.method == 'DELETE':
        try:
            remove_boot_config_definition(title)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
        return jsonify(status="ok")
    formatted_boot_config = {}
    for item in ['title', 'config']:
        formatted_boot_config[item] = getattr(boot_config, item)
    return jsonify(**formatted_boot_config)


@app.route('/api/v1/boot/', methods=['GET'])
def api_v1_boot():
    try:
        host = socket.gethostbyaddr(request.remote_addr)[0]
    except socket.herror as ex:
        return make_response(jsonify(err=str(ex)), 403)
    host = host.split('.')[0]
    machine = get_machine_definition(host)
    switch_type = machine._switch_type[machine.switch_type]
    ct = datetime.datetime.now()
    if switch_type == 'timed':
        td = datetime.timedelta(seconds=machine.time_between)
        if machine.last_boot + td > ct:
            boot_config = machine.alternate_boot
        else:
            boot_config = machine.default_boot
    elif switch_type == 'alternating':
        if machine.use_alternate:
            boot_config = machine.alternate_boot
        else:
            boot_config = machine.default_boot
        machine.use_alternate = not machine.use_alternate
    elif switch_type == 'switched':
        if machine.use_alternate:
            boot_config = machine.alternate_boot
        else:
            boot_config = machine.default_boot
    machine.last_boot = ct
    db.session.commit()
    return boot_config.config


@app.route('/api/v1/boot/finished/', methods=['GET'])
def api_v1_boot_finished():
    try:
        host = socket.gethostbyaddr(request.remote_addr)[0]
    except socket.herror as ex:
        return make_response(jsonify(err=str(ex)), 403)
    host = host.split('.')[0]
    machine = get_machine_definition(host)
    machine.use_alternate = not machine.use_alternate
    db.session.commit()
    return jsonify(status="ok")


@app.route('/machines')
def render_machines():
    return render_template('machines.html')


@app.route('/')
def render_home():
    return render_template('home.html')


@app.route('/boot_configs')
def render_boot_configs():
    return render_template('boot_configs.html')
