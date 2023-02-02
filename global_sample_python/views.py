import os

import requests
import json
from django.shortcuts import *
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt


# GET /, 결제정보 페이지 렌더링(order.html)
def order(request):
    default_data = {
        'service_id': 'demo',
        'service_oid': create_oid(),
        'comments': 'Payple global payments',
        'totalAmount': '1.00',
        'firstName': 'Payple',
        'lastName': 'Inc',
        'currency': 'USD',
        'email': 'test@payple.kr',
        'resultUrl': 'http://127.0.0.1:8000/result'
    }
    return render(request, 'order.html', default_data)


# POST /order_confirm, 결제창 호출 페이지 렌더링(order_confirm.html)
def order_confirm(request):
    if request.method == 'POST':
        return render(request, 'order_confirm.html', request.POST.dict())
    return redirect('/')


# POST /order_billingKey, 빌링키 결제 페이지 렌더링(order_billingKey.html)
def order_billingKey(request):
    if request.method == 'POST':
        return render(request, 'order_billingKey.html', request.POST.dict())
    return redirect('/')


# POST /result, 결제결과 페이지 렌더링(order_result.html)
@csrf_exempt
def order_result(request):
    if request.method == 'POST':
        print(request.POST)  # 결제결과수신

        response_data = {
            'type': request.POST.get('type'),  # 요청종류 [결제: PAYMENT | 취소: CANCEL]
            'result': request.POST.get('result'),  # 응답 코드
            'message': request.POST.get('message'),  # 응답 메시지
            'resultUrl': request.POST.get('resultUrl'),  # 결제결과 반환(Return) URL
            'api_id': request.POST.get('api_id'),  # 결제 요청 고유키
            'api_date': request.POST.get('api_date'),  # 결제 시간 (페이플 서버기준: GMT +9)
            'service_oid': request.POST.get('service_oid'),  # 주문번호
            'comments': request.POST.get('comments'),  # 상품명
            'pay_type': request.POST.get('pay_type'),  # 결제수단
            'card_number': request.POST.get('card_number'),  # 카드번호 (일부 마스킹 처리)
            'totalAmount': request.POST.get('totalAmount'),  # 결제 요청금액
            'currency': request.POST.get('currency'),  # 통화
            'firstName': request.POST.get('firstName'),  # 카드소유주 이름
            'lastName': request.POST.get('lastName'),  # 카드소유주 성
            'email': request.POST.get('email'),  # 이메일 주소
            'billing_key': request.POST.get('billing_key'),  # 빌링키 (카드정보를 암호화 한 키 값)
            'submitTimeUtc': request.POST.get('submitTimeUtc')  # 결제 시간
        }
        return render(request, 'order_result.html', response_data)


# POST /auth, 파트너 인증 API
# 1. 파트너 인증을 위한 토큰 발급은 결제요청(취소) 전 필수로 진행
# 2. 토큰의 유효기간인 10분이 지나면 요청이 거부되니 유의해주세요.
# 3. (운영) 파트너 인증 토큰발급 요청시에는 등록한 IP(White IP)와의 통신만 허용합니다.
def authenticate(request=''):
    auth_params = {
        'service_id': os.environ.get('SERVICE_ID'),  # 파트너 ID
        'service_key': os.environ.get('SERVICE_KEY'),  # 파트너 인증키
        'code': 'as12345678'  # 파트너용 토큰 확인 코드
    }

    # 파트너 인증 HTTP URL
    # TEST : https://demo-api.payple.kr/gpay/oauth/1.0/token
    # REAL : https://api.payple.kr/gpay/oauth/1.0/token
    response = requests.post('https://demo-api.payple.kr/gpay/oauth/1.0/token', data=json.dumps(auth_params),
                             headers={'Content-Type': 'application/json;', 'Cache-Control': 'no-cache'}).json()

    return HttpResponse(json.dumps(response), content_type="application/json")


# POST /payBillkey, 빌링키 결제 API
def payBillkey(request):
    if request.method == 'POST':
        auth_data = json.loads(authenticate().content)  # 파트너 인증 API 호출

        pay_req_data = json.loads(request.body)
        pay_data = {
            'service_id': os.environ.get('SERVICE_ID'),  # [필수] 파트너 ID
            'service_oid': pay_req_data.get('service_oid'),  # [선택] 주문번호
            'comments': pay_req_data.get('comments'),  # [필수] 상품명
            'billing_key': pay_req_data.get('billing_key'),  # [필수] 빌링키 (카드정보를 암호화 한 키 값)
            'securityCode': pay_req_data.get('securityCode'),  # [필수] 카드 CVC/CVV 번호
            'totalAmount': pay_req_data.get('totalAmount'),  # [필수] 결제 요청금액
            'currency': pay_req_data.get('currency'),  # [필수] 통화
            'firstName': pay_req_data.get('firstName'),  # [선택] 카드소유주 이름 (보내지 않을 경우, 최초 결제시 입력한 카드소유주 이름으로 결제요청이 됩니다.)
            'lastName': pay_req_data.get('lastName'),  # [선택] 카드소유주 성 (보내지 않을 경우, 최초 결제시 입력한 카드소유주 성으로 결제요청이 됩니다.)
            'email': pay_req_data.get('email'),  # [선택] 이메일 주소  (보내지 않을 경우, 최초 결제시 입력한 이메일 주소로 결제요청이 됩니다.)
            'resultUrl': pay_req_data.get('resultUrl')  # [선택] 해당 파라미터(resultUrl)는 별도의 기능은 하지 않으나, 파트너사에서 빌링키 결제 성공시 리다이렉트 하는 등 활용할 수 있는 파라미터입니다.
        }

        # 빌링키 결제 Request HTTP URL
        # TEST : https://demo-api.payple.kr/gpay/billingKey
        # REAL : https://api.payple.kr/gpay/billingKey
        result = requests.post('https://demo-api.payple.kr/gpay/billingKey', json.dumps(pay_data),
                               headers={'Content-Type': 'application/json;',
                                        'Cache-Control': 'no-cache',
                                        'Authorization': 'Bearer ' + auth_data.get('access_token')}).json()
        return HttpResponse(json.dumps(result), content_type="application/json")


# POST /cancel, 결제취소 API
def cancel(request):
    if request.method == 'POST':
        auth_data = json.loads(authenticate().content)  # 파트너 인증 API 호출

        cancel_req_data = json.loads(request.body)
        cancel_data = {
            'service_id': os.environ.get('SERVICE_ID'),  # [필수] 파트너 ID
            'comments': cancel_req_data.get('comments'),  # [필수] 상품명
            'service_oid': cancel_req_data.get('service_oid'),  # [필수] 주문번호
            'pay_id': cancel_req_data.get('pay_id'),  # [필수] 취소할 결제건의 api_id
            'totalAmount': cancel_req_data.get('totalAmount'),  # [필수] 결제 취소 요청금액
            'currency': cancel_req_data.get('currency'),  # [필수] 통화 (취소할 결제건의 통화로 보내야합니다)
            'resultUrl': os.environ.get('HOSTNAME') + '/result'  # [선택] 파트너사에서 취소 성공시 리다이렉트 하는 등 활용할 수 있는 파라미터입니다.
        }

        # 결제취소 Request HTTP URL
        # TEST : https://demo-api.payple.kr/gpay/cancel
        # REAL : https://api.payple.kr/gpay/cancel
        result = requests.post('https://demo-api.payple.kr/gpay/cancel', json.dumps(cancel_data),
                               headers={'Content-Type': 'application/json;',
                                        'Cache-Control': 'no-cache',
                                        'Authorization': 'Bearer ' + auth_data.get('access_token')}).json()

        return HttpResponse(json.dumps(result), content_type="application/json")


# 주문번호 생성 함수
# 리턴 예시: PaypleGpayTest-20220808090203514647
def create_oid():
    return 'PaypleGpayTest-' + datetime.now().astimezone().strftime('%Y%m%d%H%M%S%f')
