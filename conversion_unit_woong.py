#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from concurrent import futures
import time
import argparse
import grpc
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
def convert_unit(value, in_, out_):
    value = float(value)
    # 0 단위 리스트 넘버
    length = {'단위': '길이', 'unit': 'length',
              '미터': 1,
              '밀리미터': 1000, '센티미터': 100, '킬로미터': 0.001, '인치': 39.370079,
              '피트': 3.28084, '야드': 1.093613, '마일': 0.000621, '센치미터': 100,
              '미리미터': 1000, '밀리미터': 1000, '미리': 1000, '밀리': 1000, '센치': 100, '센티': 100,
              '자': 3.3, '간': 0.55, '정': 0.009167, '리': 0.002546, '해리': 0.00054}

    # 1
    data = {'단위': '데이터양', 'unit': 'data',
            '메가바이트': 1,
            '비트': 8.886808, '바이트': 1048576.0, '킬로바이트': 1024.0, '기가바이트': 0.000977,
            '테라바이트': 0.00000095367, '페타바이트': 0.00000000093132, '엑사바이트': 0.00000000000090949}

    # 2
    weight = {'단위': '무게', 'unit': 'weight',
              '킬로그램': 1,
              '밀리그램': 1000000, '그램': 1000, '톤': 0.001, '킬로톤': 0.0000001, '그레인': 15432.3584,
              '온스': 35.273962, '파운드': 2.204623, '돈': 266.66666666, '근': 1.66666666,
              '트로이온스': 32.10347680, '그람': 1000, '킬로그람': 1, '밀리그람': 1000000}

    # 3
    temperature = {'단위': '온도', 'unit': 'temperature',
                   '섭씨온도': 1,
                   '화씨온도': 33.8, '절대온도': 274.15, '섭씨': 1, '화씨': 33.8}

    # 4
    area = {'단위': '넓이', 'unit': 'area',
            '평': 1,
            '제곱미터': 3.305785, '아르': 0.033058, '헥타르': 0.000311,
            '제곱킬로미터': 0.00033058, '제곱피트': 35.583175,
            '제곱야드': 3.953686, '에이커': 0.000817}

    # 5
    volume = {'단위': '부피', 'unit': 'volume',
              '리터': 1,
              '시시': 1000, '씨씨': 1000, 'cc': 1000, '밀리리터': 1000, '미리리터': 1000, '데시리터': 10,
              '세제곱센티미터': 1000, '세제곱센치미터': 1000, '세제곱미터': 0.001, '세제곱인치': 61.023744,
              '세제곱피트': 0.035315, '세제곱야드': 0.001308, '갤런': 0.254172, '배럴': 0.006293, '온스': 33.814022
              '홉': 5.543545, '되': 0.554354, '말': 0.055435}

    # 6
    atom_pressure = {'단위': '압력', 'unit': 'atom_pressure',
                     '기압': 1,
                     '파스칼': 101325, '헥토파스칼': 1013.25,
                     '킬로파스칼': 101.325, '메가파스칼': 0.101325,
                     '밀리바': 1013.25, '바': 1.01325, '프사이': 14.696,
                     '수은주밀리미터': 760, '수주밀리미터': 10332.275}

    # 단위 리스트
    unit_list = [length, data, weight, temperature, area, volume, atom_pressure]

    # 은/는 비교해서 넣어줄 리스트
    josa_list = ['간', '정', '밀리그램', '그램', '킬로그램', '톤', '킬로톤', '그레인', '돈', '근',
                 '그람', '킬로그람', '밀리그람', '평', '갤런', '파스칼', '헥토파스칼', '킬로파스칼',
                 '메가파스칼', '데이터양', '압력']

    result = 0

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
        # print in_unit['단위'] + "을 " + out_unit['단위'] + "으로 변환할 수 없습니다."
        # info_text = in_unit['단위'] + "을 " + out_unit['단위'] + "으로 변환할 수 없습니다."
        # return info_text
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

        result.params.extend(params)
        return result



    def Talk(self, talk, context):
        self.get_sds_server()
        session_id = talk.session_id
        print "Session ID : " + str(session_id)
        print "[Question] ", talk.text

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
        sq.utter = talk.text

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
            infotext = convert_unit(value, inputunit, outputunit)
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
