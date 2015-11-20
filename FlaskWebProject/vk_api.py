import time
import logging
import requests

logger = logging.getLogger(__name__)

PROFILE_FIELDS = ['nickname', 'screen_name', 'sex', 'bdate', 'city', 'relation', 'country', 'home_town',
                  'education', 'universities',   'schools',  'occupation'
                  'connections', 'relation', 'relatives', 
                  'interests', 'books', 'last_seen', 'counters', ] 
				  
class JsonUtils(object):
    @staticmethod
    def json_path(json, path, default=u''):
        splited = path.split(u'.')
        for p in splited:
            try:
                p_id = int(p)
                json = json[p_id]
            except:
                if p in json:
                    json = json[p]
                else:
                    return default
        return json.unicode

class VkError(Exception):    
    pass
    
class VkAPI(object):    
         
    def __init__(self, token=None):
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        self.token = token
        self.requests_times = []
        
    def _do_api_call(self, method, params):
        self._pause_before_request()
        
        if self.token:
            params['access_token'] = self.token
        params['v'] = '5.26'
            
        param_str = '&'.join(['%s=%s' % (k, v) for k, v in params.iteritems()])
        url = 'https://api.vk.com/method/%s?%s' % (method, param_str)
        logger.debug('API request: %s' % (method))
        
        response = self.session.get(url)
        if response.status_code is not 200:
            time.sleep(10)
            response = self.session.get(url)
            if response.status_code is not 200:
                raise VkError('Can\'t get %s, code %s' % (url, response.status_code))        
                
        json = response.json()
        if 'response' not in json:
            if 'error' in json:   
                raise VkError('Api call error:  %s' % json['error']['error_msg'])                
            else:
                raise VkError('Api call error %s - %s' % (url, json))
                        
        return json['response'] 
        
    def _pause_before_request(self):
        if len(self.requests_times) > 2:
            first = self.requests_times[0]
            diff = time.time() - first
            if diff < 1.:
                logger.info('Sleepping for %s sec' % (1.2 - diff))
                time.sleep(1.- diff)
            self.requests_times = self.requests_times[1:]            
        self.requests_times.append(time.time())
        
    def get_user_profile(self, user_id, fields=PROFILE_FIELDS):    
        profile = self._do_api_call('users.get', { 'user_ids' :  user_id,  'fields' : ','.join(fields)})                    
        return profile[0]           
                            
    def get_user_profiles(self, user_ids, fields=PROFILE_FIELDS):                      
        result = []        
        for offset in range(0, len(user_ids) / 100 + 1):
            start, end = offset * 100, (offset + 1) * 100 
            ids = ','.join([str(user_id) for user_id in user_ids[start:end]])        
            response = self._do_api_call('users.get', { 'user_ids' :  ids,  'fields' : ','.join(fields)})
            result.extend(response)
        return result
    
    def get_friends(self, user_id, fields = []):
        response = self._do_api_call('friends.get', { 'user_id' : user_id,   'fields' : ','.join(fields)})                    
        return response['items']
                    
    def close(self):
        self.session.close()        

    def get_user_network(self, user_id, depth):          
        all_profiles = dict()
        logger.info('Getting profile for id%s' % user_id)
        all_profiles[user_id] = self.get_user_profile(user_id)
        
        queue = [(user_id, depth)]       
        while len(queue) > 0:
            head_id, head_depth = queue[0]        
            logger.info('Getting friends for id%s' % head_id)   
            friends = []
            try:
                friends = self.get_friends(head_id, fields=[])    
            except VkError as e:
                pass            
            all_profiles[head_id]['friends'] = friends
            
            if head_depth > 1:            
                for friend_id in friends:                    
                    if friend_id not in all_profiles:
                        all_profiles[friend_id] = {'id' : friend_id }
                        queue.append((friend_id, head_depth - 1))
            queue.pop(0) 
        return all_profiles 