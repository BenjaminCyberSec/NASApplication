from expiringdict import ExpiringDict


#This class is used by the custom wrapper of FieldFile, namely EncryptedFile
#Since it is impossible to sent parameters to that wrapper in a convenient way
#The keys are stored for a short amount of time in this class 
class TemporaryKeyHandler(object):
    
    _user_cache = ExpiringDict(max_len=500, max_age_seconds=10) #user : key
    _file_cache = ExpiringDict(max_len=1000, max_age_seconds=10) #file : user
    _shared_file_cache = ExpiringDict(max_len=500, max_age_seconds=10) #file : group_key
  
    #link a key to an user for the time of the operation
    @classmethod
    def addUser(cls,user,key):
        print(user)
        cls._user_cache[user] = key

    #link a file to a user for a very short time 
    # (just enough time to encrypt the file with the proper user key in the EncryptedFile model which is
    # a wrapper of FieldFile that can't be given parameters in an usual way)
    @classmethod
    def addFile(cls,user,file):
        cls._file_cache[file] = user
        
    

    #link a file to a group_key for a very short time 
    # (just enough time to encrypt the file with the proper group key in the EncryptedFile model which is
    # a wrapper of FieldFile that can't be given parameters in an usual way)
    @classmethod
    def addSharedFile(cls,key,file):
        cls._shared_file_cache[file] = key

    @classmethod
    def getFileKey(cls,file):
        print(file)
        print(cls._user_cache)
        print(cls._file_cache)
        if file in cls._file_cache:
            user = cls._file_cache.get(file)
            if user in cls._user_cache:
                return cls._user_cache.get(user)
            else:
                print("session has expired")
                return False
        else:
            if file in cls._shared_file_cache:
                return cls._shared_file_cache.get(file)
            else:
                print("unknown issue")
                return False
