from flask import request, jsonify, current_app
from .utils import getauth,check_event_loop_status,setEHRbasepaths,insertlogline
from .security import create_jwt_token,verify_jwt_token
from .ehrbase_methods import get_dashboard_data_ehrbase,get_sidebar_ehrs_ehrbase,get_sidebar_templates_ehrbase,get_sidebar_compositions_ehrbase,get_sidebar_queries_ehrbase,get_ehr_by_ehrid_ehrbase
from .config import get_config
# from .myredis import init_redis
from .ehrbase_methods import get_dashboard_data_ehrbase,get_sidebar_ehrs_ehrbase,get_sidebar_templates_ehrbase,get_sidebar_compositions_ehrbase,get_sidebar_queries_ehrbase,get_ehr_by_ehrid_ehrbase
import httpx

def load_routes(app):

    @app.route('/test', methods=['GET'])
    async def test():
        return jsonify({"message": "Hello, World!"}), 200
    
    @app.route('/login', methods=['POST','GET'])
    async def login():
        # global auth,url_base,url_base_ecis,url_base_admin,url_base_management,url_base_status,username,ehrbase_version
        if request.method == 'GET':
            return jsonify({"message": "This is a GET request"})
        current_app.logger.debug('login')
        print('aaaaaaaaaaa')
        data = request.json
        username = data.get('username')
        password = data.get('password')
        auth=getauth(username,password)
        current_app.config['AUTH'] = auth
        input_url = data.get('url')


        # # Check if the username exists
        # if username not in users:
        #     return jsonify({"message": "Invalid username or password"}), 401

        # Validate against the foo server using the provided URL
        try:
            client = current_app.config['HTTPX_CLIENT']
            if check_event_loop_status() == 'ok':
                print('Event loop is running.')
            else:
                client = httpx.AsyncClient()
                current_app.config['HTTPX_CLIENT'] = client
            response = await client.get(input_url + "rest/status", headers={'Authorization':auth,'Content-Type':'application/json', 'Accept': 'application/json'})
            print('response')
            print(response.status_code)
            print(response.json())

            if response.status_code == 200:
                ehrbase_version=response.json()['ehrbase_version']
                # Generate a token (this is just a mock, you should use JWT or something more secure)
                print('a2')
                url_base,url_base_ecis,url_base_admin,url_base_management,url_base_status=setEHRbasepaths(input_url)
                print('a2_1')
                current_app.config['URL_BASE'] = url_base
                current_app.config['URL_BASE_ECIS'] = url_base_ecis
                current_app.config['URL_BASE_ADMIN'] = url_base_admin
                current_app.config['URL_BASE_MANAGEMENT'] = url_base_management
                current_app.config['URL_BASE_STATUS'] = url_base_status
                current_app.config['EHRBASE_VERSION'] = ehrbase_version
                print('a2_2')
                token=create_jwt_token(username)
                #read config
                print('a3')
                nodename,redishostname,redisport=get_config()
                current_app.config['NODENAME'] = nodename
                # print('a4')
                # #init_redis
                # current_app.config['REDIS_CLIENT'] = init_redis(redishostname,redisport)
                # print('a5')
                #create lists of EHRs, Compositions,Templates, AQLs
                # save them to redis
                return jsonify({"token": token}), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        except Exception as e:
          print(f"An exception occurred during login: {e}")
          return jsonify({"message": "Server error during login"}), 500

    @app.route('/dashboard', methods=['GET'])
    async def get_dashboard_data():
        current_app.logger.debug('dashboard route')
        tokeninauthheader = request.headers.get('Authorization')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            return jsonify({"message": "Unauthorized"}), 401
        print('bbbbbbbbbbb')
        # This route should only be accessible with a valid token.
        # Simulate fetching methods from the server
        # await asyncio.sleep(1)
        # return jsonify({'dashboard_data': {'barData': {'1': 1, '2': 9, '3': 1, '4': 1, '9': 1, '41': 1}, 'info': {'archie_version': '3.12.0', 'ehrbase_version': '2.15.0', 'jvm_version': 'Eclipse Adoptium 21.0.6+7-LTS', 'openehr_sdk_version': '2.21.0', 'os_version': 'Linux amd64 5.15.0-131-generic', 'postgres_version': 'PostgreSQL 16.2 on x86_64-pc-linux-musl, compiled by gcc (Alpine 13.2.1_git20231014) 13.2.1 20231014, 64-bit'}, 'metrics': {'aqlsCount': 1, 'compositionsCount': 76, 'ehrsCount': 17, 'ehrsInUse': 17, 'templatesCount': 8, 'templatesInUse': 3}, 'pieData': {'BBMRI-ERIC_Colorectal_Cancer_Cohort_Report': 1, 'Interhealth_cancer_registry': 74, 'testinterval': 1}}}), 200
        try:
            url_base=current_app.config.get('URL_BASE')
            url_base_status=current_app.config.get('URL_BASE_STATUS')
            url_base_management=current_app.config.get('URL_BASE_MANAGEMENT')
            metrics,barData,pieData,info=await get_dashboard_data_ehrbase(auth,url_base,url_base_status,url_base_management)
            #metrics: aqlsCount,ehrsCount,compositionsCount,templatesCount,templatesInUse,ehrsInUse
            #info:  ehrbase_version, openehr_sdk_version, archie_version, jvm_version,os_version,postgres_version
            return jsonify({"dashboard_data": {"metrics":metrics,"barData":barData,"pieData":pieData,"info":info}}), 200
        except Exception as e:
            print(f"An exception occurred during get_dashboard_data: {e}")
            return jsonify({"message": "Server error during get_dashboard_data"}), 500

    @app.route('/rsidebar/ehrs', methods=['GET'])
    async def get_sidebar_ehrs():
        current_app.logger.debug('get sidebar ehrs')
        tokeninauthheader = request.headers.get('Authorization')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401        
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            return jsonify({"message": "Unauthorized"}), 401
        print('bbbbbbbbbbb')
        try:
            url_base=current_app.config.get('URL_BASE')
            ehrs=await get_sidebar_ehrs_ehrbase(auth,url_base)
            print(ehrs)
            return jsonify({"ehrs": ehrs}), 200
        except Exception as e:
            print(f"An exception occurred during get_sidebar_ehrs: {e}")
            return jsonify({"message": "Server error during get_sidebar_ehrs"}), 500

    @app.route('/rsidebar/templates', methods=['GET'])
    async def get_sidebar_templates():
        current_app.logger.debug('get sidebar templates')
        tokeninauthheader = request.headers.get('Authorization')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401        
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            return jsonify({"message": "Unauthorized"}), 401
        print('cccccccccccc')
        try:
            url_base=current_app.config.get('URL_BASE')
            templates=await get_sidebar_templates_ehrbase(auth,url_base)
            return jsonify({"templates": templates}), 200
        except Exception as e:
            print(f"An exception occurred during get_sidebar_templates: {e}")
            return jsonify({"message": "Server error during get_sidebar_templates"}), 500        

    @app.route('/rsidebar/compositions', methods=['GET'])
    async def get_sidebar_compositions():
        current_app.logger.debug('get sidebar compositions')
        tokeninauthheader = request.headers.get('Authorization')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401        
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            return jsonify({"message": "Unauthorized"}), 401
        print('bbbbbbbbbbb')
        try:
            url_base=current_app.config.get('URL_BASE')
            compositions=await get_sidebar_compositions_ehrbase(auth,url_base)
            return jsonify({"compositions": compositions}), 200
        except Exception as e:
            print(f"An exception occurred during get_sidebar_compositions: {e}")
            return jsonify({"message": "Server error during get_sidebar_compositions"}), 500

    @app.route('/rsidebar/queries', methods=['GET'])
    async def get_sidebar_queries():
        current_app.logger.debug('get sidebar queries')
        tokeninauthheader = request.headers.get('Authorization')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401        
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            return jsonify({"message": "Unauthorized"}), 401
        print('bbbbbbbbbbb')
        try:
            url_base=current_app.config.get('URL_BASE')
            queries=await get_sidebar_queries_ehrbase(auth,url_base)
            return jsonify({"queries": queries}), 200
        except Exception as e:
            print(f"An exception occurred during get_sidebar_queries: {e}")
            return jsonify({"message": "Server error during get_sidebar_queries"}), 500 

    @app.route('/ehr/<string:ehrid>', methods=['GET'])
    async def get_ehr_by_ehrid(ehrid):
        current_app.logger.debug('ehr: get ehr by ehrid')
        tokeninauthheader = request.headers.get('Authorization')
        print(f'tokeninauthheader: {tokeninauthheader}')
        if not tokeninauthheader:
            return jsonify({"message": "Unauthorized"}), 401        
        token = tokeninauthheader.split('Bearer ')[1]
        auth=current_app.config.get('AUTH')
        if not verify_jwt_token(token) or not auth:
            print('dentro not verify')
            print(verify_jwt_token(token))
            print(auth)
            return jsonify({"message": "Unauthorized"}), 401
        print('bbbbbbbbbbb')
        try:
            url_base=current_app.config.get('URL_BASE')
            response=await get_ehr_by_ehrid_ehrbase(auth,url_base,ehrid)
            if response['status'] == 'success':
                insertlogline('Get EHR by ehrid: ehr '+ehrid+' retrieved successfully')
            return jsonify({"ehr": response['ehr']}), 200
        except httpx.TimeoutException:
            print("The request timed out")
            return jsonify({"message": "The request timed out"}), 504
        except Exception as e:
            print(f"An exception occurred during get ehr by ehrid: {e}")
            return jsonify({"message": "Server error during get ehr by ehrid"+str(e)}), 500            

