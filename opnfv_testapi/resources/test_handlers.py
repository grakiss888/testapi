##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import logging
from datetime import datetime
from datetime import timedelta
import json

from bson import objectid


from tornado import web
from tornado import gen

from opnfv_testapi.common.config import CONF
from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import result_handlers 
from opnfv_testapi.resources import test_models
from opnfv_testapi.tornado_swagger import swagger
from opnfv_testapi.ui.auth import constants as auth_const
from opnfv_testapi.db import api as dbapi


class GenericTestHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericTestHandler, self).__init__(application,
                                                   request,
                                                   **kwargs)
        self.table = self.db_tests
        self.table_cls = test_models.Test

    def get_int(self, key, value):
        try:
            value = int(value)
        except:
            raises.BadRequest(message.must_int(key))
        return value

    def set_query(self):
        query = dict()
        date_range = dict()
        for k in self.request.query_arguments.keys():
            v = self.get_query_argument(k)
            if k == 'period':
                v = self.get_int(k, v)
                if v > 0:
                    period = datetime.now() - timedelta(days=v)
                    obj = {"$gte": str(period)}
                    query['start_date'] = obj
            elif k == 'from':
                date_range.update({'$gte': str(v)})
            elif k == 'to':
                date_range.update({'$lt': str(v)})
            elif k == 'signed':
                openid = self.get_secure_cookie(auth_const.OPENID)
                role = self.get_secure_cookie(auth_const.ROLE)
                logging.info('role:%s', role)
                if role:
                    query['owner'] = openid
                    if role == "reviewer":
                        del query['owner']
                        query['$or'] = [{"shared": {"$elemMatch": {"$eq": openid}}}, \                                                                     {"owner": openid}, {"status": {"$ne": "private"}}]
                    else:
                        query['$or'] = [{"shared":{"$elemMatch":{"$eq":openid}}},{"owner":openid}] 
            elif k not in ['last', 'page', 'descend']:
                query[k] = v
            if date_range:
                query['start_date'] = date_range

            # if $lt is not provided,
            # empty/None/null/'' start_date will also be returned
            if 'start_date' in query and '$lt' not in query['start_date']:
                query['start_date'].update({'$lt': str(datetime.now())})

        return query


class TestsCLHandler(GenericTestHandler):
    @swagger.operation(nickname="queryTests")
    def get(self):
        """
            @description: Retrieve result(s) for a test project
                          on a specific pod.
            @notes: Retrieve result(s) for a test project on a specific pod.
                Available filters for this request are :
                 - id  : Test id
                 - period : x last days, incompatible with from/to
                 - from : starting time in 2016-01-01 or 2016-01-01 00:01:23
                 - to : ending time in 2016-01-01 or 2016-01-01 00:01:23
                 - signed : get logined user result

                GET /results/project=functest&case=vPing&version=Arno-R1 \
                &pod=pod_name&period=15&signed
            @return 200: all test results consist with query,
                         empty list if no result is found
            @rtype: L{Tests}
        """
        def descend_limit():
            descend = self.get_query_argument('descend', 'true')
            return -1 if descend.lower() == 'true' else 1

        def last_limit():
            return self.get_int('last', self.get_query_argument('last', 0))

        def page_limit():
            return self.get_int('page', self.get_query_argument('page', 0))

        limitations = {
            'sort': {'_id': descend_limit()},
            'last': last_limit(),
            'page': page_limit(),
            'per_page': CONF.api_results_per_page
        }

        self._list(query=self.set_query(), **limitations)

    @swagger.operation(nickname="createTest")
    def post(self):
        """
            @description: create a test
            @param body: test to be created
            @type body: L{TestCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: test is created.
            @raise 404: pod/project/testcase not exist
            @raise 400: body/pod_name/project_name/case_name not provided
        """
        openid = self.get_secure_cookie(auth_const.OPENID)
        if openid:
            self.json_args['owner'] = openid

        self._post()

    def _post(self):
        miss_fields = []
        carriers = []

        self._create(miss_fields=miss_fields, carriers=carriers)

class DownloadHandler(web.RequestHandler):
    @swagger.operation(nickname='downloadLogsById')
    def get(self, test_id):
        path = '/home/testapi/logs/'
        filename = 'log_%s.tar.gz' % (test_id)
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + filename)
        with open(path+filename, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()


class TestsGURHandler(GenericTestHandler):
    @swagger.operation(nickname="updateTestById")
    def put(self, test_id):
        """
            @description: update a single test by id
            @param body: fields to be updated
            @type body: L{TestUpdateRequest}
            @in body: body
            @rtype: L{Test}
            @return 200: update success
            @raise 404: Test not exist
            @raise 403: nothing to update
        """
        data = json.loads(self.request.body)
        item = data.get('item')
        value = data.get(item)
        logging.debug('%s:%s', item, value)
        try:
            self.update(test_id, item, value)
        except Exception as e:
            logging.error('except:%s', e)
            return

    @web.asynchronous
    @gen.coroutine
    def update(self, test_id, item, value):
        if item == "shared":
            for user in value:
                logging.debug('user:%s', user)
                query = {"openid":user}
                data = yield dbapi.db_find_one("users", query)
                if not data:
                    logging.debug('not found')
                    raises.NotFound(message.not_found('users', query))
        self.json_args = {}
        self.json_args[item] = value
        query = {'id': test_id, 'owner': self.get_secure_cookie(auth_const.OPENID)}
        db_keys = ['id', 'owner']
        self._update(query=query, db_keys=db_keys)
