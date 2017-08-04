#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from concurrent import futures
import time
import argparse
import grpc
import pymysql
from google.protobuf import empty_pb2

import os
exe_path = os.path.realpath(sys.argv[0])
bin_path = os.path.dirname(exe_path)
lib_path = os.path.realpath(bin_path + '/../lib/python')
sys.path.append(lib_path)

from proto import pool_pb2
from proto import sds_pb2
from proto import provider_pb2
from proto import userattr_pb2

# import MySQLdb.cursors

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


# 단위 변환 함수
def convert_unit(value, in_, out_, curs):
    value = float(value)

    # 단위 DB 호출
    query = 'select * from conversion_unit'
    content = ''
    unit_list = list()
    curs.execute(query)
    rows = curs.fetchall()

    if curs.rowcount != 0:
        for row in rows:
            for k in row.keys():
                if k == 'content':
                    content = row.get(k)
            unit_list.append(eval('{' + content + '}'))

    # 은/는 비교해서 넣어줄 리스트
    josa_list = ['간', '정', '밀리그램', '그램', '킬로그램', '톤', '킬로톤', '그레인', '돈', '근',
                 '그람', '킬로그람', '밀리그람', '평', '갤런', '파스칼', '헥토파스칼', '킬로파스칼',
                 '메가파스칼', '데이터양', '압력', '홉', '말']
    try :
        for units in unit_list:
            if in_ in units:
                in_unit = units
                print in_unit['unit']
            if out_ in units:
                out_unit = units
                print out_unit['unit']

        if in_unit == out_unit:
            meters = (value / in_unit[in_])
            result = round(meters * in_unit[out_], 4)
            print meters, "meters -----------"
            print result, "result ------------"
            print type(value), type(result)

            value = format(dot(value), ',')
            result = format(dot(result), ',')

            if in_ in josa_list:
                info_text = str(value) + in_ + '은 ' # 받침 o
            else:
                info_text = str(value) + in_ + '는 ' # 받침 x
                print 'result = ', result

            info_text += str(result) + str(out_) + ' 입니다'

            return info_text

        elif in_unit != out_unit:
            info_text = ''
            if in_unit['단위'] in josa_list:
                info_text = in_unit['단위'] + '을 ' # 받침 o
            else:
                info_text = in_unit['단위'] + '를 ' # 받침 x

            if out_unit['단위'] in josa_list:
                b = out_unit['단위'] + '으로 ' # 받침 o
            else:
                b = out_unit['단위'] + '로 ' # 받침 x

            info_text += b + '변환할 수 없습니다.'
            return info_text

        else:
            print "정확히 입력해주세요."
            info_text = "정확히 입력해주세요."
            return info_text

    except:
        info_text = '정확히 입력해주세요.'
        return info_text


# float 변수에서 소숫점이 .0일 경우 int로 출력해주는 함수
def dot(number):
    if int(number) == number:
        return int(number)
    else:
        return number


class conversion_unitDA(provider_pb2.DialogAgentProviderServicer):
    # STATE
    # state = provider_pb2.DIAG_STATE_IDLE
    init_param = provider_pb2.InitParameter()

    # PROVIDER
    provider = pool_pb2.DialogAgentProviderParam()
    provider.name = 'conversion_unit'
    provider.description = '단위 변환'
    provider.version = '0.1'
    provider.single_turn = True
    provider.agent_kind = pool_pb2.AGENT_SDS
    provider.require_user_privacy = True

    # PARAMETER

    # SDS Stub
    sds_server_addr = ''
    sds_stub = None

    # dm2.tutor.mindslab.ai
    # ubuntu 사용자로 접속
    # images.docker / volumes / dm-8021 / www_data / project / HealthCare_Recommend_SeasonalFood


    def __init__(self):
        self.state = provider_pb2.DIAG_STATE_IDLE

    #
    # INIT or TERM METHODS
    #

    def get_sds_server(self):
        sds_channel = grpc.insecure_channel(self.init_param.sds_remote_addr)
        # sds_channel = grpc.insecure_channel('127.0.0.1:9906')
        resolver_stub = sds_pb2.SpokenDialogServiceResolverStub(sds_channel)

        print 'stub'
        sq = sds_pb2.ServiceQuery()
        sq.path = self.sds_path
        sq.name = self.sds_domain
        print sq.path, sq.name

        svc_loc = resolver_stub.Find(sq)
        print 'find result', svc_loc
        # Create SpokenDialogService Stub
        print 'find result loc: ', svc_loc.server_address
        self.sds_stub = sds_pb2.SpokenDialogServiceStub(
            grpc.insecure_channel(svc_loc.server_address))
        self.sds_server_addr = svc_loc.server_address
        print 'stub sds ', svc_loc.server_address

    def IsReady(self, empty, context):
        print 'IsReady', 'called'
        status = provider_pb2.DialogAgentStatus()
        status.state = self.state
        return status

    def Init(self, init_param, context):
        print 'Init', 'called'
        self.state = provider_pb2.DIAG_STATE_INITIALIZING
        # COPY ALL
        self.init_param.CopyFrom(init_param)
        # DIRECT METHOD
        self.sds_path = init_param.params['sds_path']
        print 'path'
        self.sds_domain = init_param.params['sds_domain']
        print 'domain'

        # DB
        self.db_host = init_param.params['db_host']
        print 'db_host'

        self.db_port = init_param.params["db_port"]
        print 'db_port'

        self.db_user = init_param.params['db_user']
        print 'db_user'

        self.db_pwd = init_param.params['db_pwd']
        print 'db_pwd'

        self.db_database = init_param.params['db_database']
        print 'db_database'

        self.db_table = init_param.params['db_table']
        print 'db_table'

        # CONNECT
        self.get_sds_server()
        print 'sds called'
        self.state = provider_pb2.DIAG_STATE_RUNNING
        # returns provider
        result = pool_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        print 'result called'
        return result

    def Terminate(self, empty, context):
        print 'Terminate', 'called'
        # DO NOTHING
        self.state = provider_pb2.DIAG_STATE_TERMINATED
        return empty_pb2.Empty()

    #
    # PROPERTY METHODS
    #
    def GetProviderParameter(self, empty, context):
        print 'GetProviderParameter', 'called'
        result = pool_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        return result

    def GetRuntimeParameters(self, empty, context):
        print 'GetRuntimeParameters', 'called'
        params = []
        result = provider_pb2.RuntimeParameterList()

        sds_path = provider_pb2.RuntimeParameter()
        sds_path.name = 'sds_path'
        sds_path.type = userattr_pb2.DATA_TYPE_STRING
        sds_path.desc = 'DM Path'
        sds_path.default_value = 'conversion_unit_woong' # ---
        sds_path.required = True
        params.append(sds_path)

        sds_domain = provider_pb2.RuntimeParameter()
        sds_domain.name = 'sds_domain'
        sds_domain.type = userattr_pb2.DATA_TYPE_STRING
        sds_domain.desc = 'DM Domain'
        sds_domain.default_value = 'conversion_unit_woong' # ---
        sds_domain.required = True
        params.append(sds_domain)

        #DB
        db_host = provider_pb2.RuntimeParameter()
        db_host.name = 'db_host'
        db_host.type = userattr_pb2.DATA_TYPE_STRING
        db_host.desc = 'Database Host'
        # db_host.default_value = '40.71.194.77'u
        # db_host.default_value = '52.187.6.21'
        db_host.default_value = '10.122.64.134'
        db_host.required = True
        params.append(db_host)

        db_port = provider_pb2.RuntimeParameter()
        db_port.name = 'db_port'
        db_port.type = userattr_pb2.DATA_TYPE_STRING
        db_port.desc = 'Database Port'
        db_port.default_value = '3306'
        db_port.required = True
        params.append(db_port)

        db_user = provider_pb2.RuntimeParameter()
        db_user.name = 'db_user'
        db_user.type = userattr_pb2.DATA_TYPE_STRING
        db_user.desc = 'Database User'
        # db_user.default_value = 'tutor'
        db_user.default_value = 'minds'
        db_user.required = True
        params.append(db_user)

        db_pwd = provider_pb2.RuntimeParameter()
        db_pwd.name = 'db_pwd'
        db_pwd.type = userattr_pb2.DATA_TYPE_STRING
        db_pwd.desc = 'Database Password'
        # db_pwd.default_value = 'ggoggoma'
        db_pwd.default_value = 'ggoggoma67'
        db_pwd.required = True
        params.append(db_pwd)

        db_database = provider_pb2.RuntimeParameter()
        db_database.name = 'db_database'
        db_database.type = userattr_pb2.DATA_TYPE_STRING
        db_database.desc = 'Database Database name'
        db_database.default_value = 'ascar'
        db_database.required = True
        params.append(db_database)

        db_table = provider_pb2.RuntimeParameter()
        db_table.name = 'db_table'
        db_table.type = userattr_pb2.DATA_TYPE_STRING
        db_table.desc = 'Database table'
        db_table.default_value = 'conversion_unit'
        db_table.required = True
        params.append(db_table)

        result.params.extend(params)
        return result



    def Talk(self, talk, context):
        conn = pymysql.connect(user='minds',
                               password='ggoggoma67',
                               host='10.122.64.134',
                               database='ascar',
                               charset='utf8',
                               use_unicode=False)

        curs = conn.cursor(pymysql.cursors.DictCursor)

        self.get_sds_server()
        session_id = talk.session_id
        print "Session ID : " + str(session_id)
        print "[Question] ", talk.text

        # 가정 -> 정 예외처리 ex) 미터가 정으로 얼마야
        input_text = talk.text
        input_text = input_text.replace("가정", "정")

        if talk.text[-3:] == '평이야':
            talk.text = talk.text[:-3] + '평이니'

        #
        # STEP #1
        #

        # Create DialogSessionKey & set session_key
        dsk = sds_pb2.DialogueSessionKey()
        dsk.session_key = session_id

        # Dialog Open
        sds_sessions = self.sds_stub.Open(dsk)

        sq = sds_pb2.SdsQuery()
        sq.session_key = sds_sessions.session_key
        # sq.utter = talk.text
        sq.utter = input_text

        # Dialog UnderStand
        sds_act = self.sds_stub.Understand(sq)


        s = sds_act.origin_best_slu.find('(')
        e = sds_act.origin_best_slu.find(',')
        sub_cmd = sds_act.origin_best_slu[s + 1:e]
        print '[SLU1 Request] ', sub_cmd

        # Create sds_slots & set Session Key
        sds_slots = sds_pb2.SdsSlots()
        sds_slots.session_key = sds_sessions.session_key

        value = 1
        inputunit = ''
        outputunit = ''
        result = 0
        # Copy filled_slot to result Slot & Fill information slots
        for k, v in sds_act.filled_slots.items():
            sds_slots.slots[k] = v

        if sds_act.filled_slots.get('unit.value') is not None:
            value = sds_act.filled_slots.get('unit.value').encode('utf-8')
            print '[value] = ', value

        if sds_act.filled_slots.get('unit.first') is not None:
            inputunit = sds_act.filled_slots.get('unit.first').encode('utf-8')
            print '[inputunit] = ', inputunit

        if sds_act.filled_slots.get('unit.second') is not None:
            outputunit = sds_act.filled_slots.get('unit.second').encode('utf-8')
            print '[outputunit] = ', outputunit

        print '[main] value = ', value
        print '[main] inputunit = ', inputunit
        print '[main] outputunit = ', outputunit

        print '====================================================================='
        # print '[sds_pb2.SdsQuery()] = ', sq
        # print '[sds_act.success] = ', sds_act.success
        # print '[sds_act.finished] = ', sds_act.finished
        # print '[sds_act.origin_best_slu] = ', sds_act.origin_best_slu
        # print '[sds_act.response] = ', sds_act.response
        # print '[sds_act.status] = ', sds_act.status
        # print '[sds_act.act] = ', sds_act.act
        # print '[sds_act.origin_slu] = ', sds_act.origin_slu
        # print '[SdsUtter.success] = ', sds_pb2.SdsUtter.success
        # print '[SdsUtter.response] = ', sds_pb2.SdsUtter.response
        # print '[SdsUtter.status] = ', sds_pb2.SdsUtter.status
        # print '[sds_act.origin_slot] = ', sds_act.origin_slot
        print '====================================================================='

        if value != 0 or inputunit != '' or outputunit != '': # 단위변환 함수 호출
            infotext = convert_unit(value, inputunit, outputunit, curs)
            # result = convert_unit(value, inputunit, outputunit)

        else:
            infotext = '잘 못 입력하셨습니다. 다시 입력해주시기 바랍니다.'


        # result = convert_unit(value, inputunit, outputunit)

        print '[result] infotext = ', infotext
        print '[result] infotext = ', type(infotext)
        sds_slots.slots['unit.infotext'] = infotext

        # sds_slots.slots['unit.result'] = str(result)

        #
        # STEP3
        # Sedn result slot & Get response
        sdsUtter = self.sds_stub.FillSlots(sds_slots)
        #
        # STEP4
        #

        print "[System output] infotext : " + infotext
        talk_res = provider_pb2.TalkResponse()
        talk_res.text = infotext
        # talk_res.text = sdsUtter.response
        talk_res.state = provider_pb2.DIAG_CLOSED
        self.sds_stub.Close(dsk)

        curs.close()
        conn.close()

        return talk_res

    def Close(self, req, context):
        print 'Closing for ', req.session_id, req.agent_key
        talk_stat = provider_pb2.TalkStat()
        talk_stat.session_key = req.session_id
        talk_stat.agent_key = req.agent_key

        ses = sds_pb2.DialogueSessionKey()
        ses.session_key = req.session_id
        self.sds_stub.Close(ses)
        return talk_stat


def serve():
    parser = argparse.ArgumentParser(description='conversion_unit DA')
    parser.add_argument('-p', '--port',
                        nargs='?',
                        dest='port',
                        required=True,
                        type=int,
                        help='port to access server')
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2.add_DialogAgentProviderServicer_to_server(conversion_unitDA(), server)

    listen = '[::]' + ':' + str(args.port)
    server.add_insecure_port(listen)

    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

