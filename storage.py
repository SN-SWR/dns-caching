from time import time
import os
import pickle


class CacheStorage:
    def __init__(self, filename):
        self.filename = filename
        self.filepath = os.path.join(os.getcwd(), self.filename)
        self.storage = {}
        if os.path.exists(self.filepath):
            self.load()

    def save(self):
        with open(self.filepath, 'wb') as f:
            pickle.dump(self.storage, f)

    def load(self):
        with open(self.filepath, 'rb') as f:
            load = pickle.load(f)
            clear_keys = []
            for key in load.keys():
                for entity in load[key]:
                    if entity[0]['Ttl'] + entity[1] < time():
                        clear_keys.append(key)
                        break
            for key in clear_keys:
                load.pop(key)
            self.storage = load

    def get_entity(self, parsed_data):
        result = []
        for question in parsed_data[1]:
            entity = self.storage.get((question['Name'], question['Type']))
            if entity is not None:
                for answer in entity:
                    if answer[0]['Ttl'] + answer[1] > time():
                        answer[0]['Ttl'] = answer[1] + answer[0][
                            'Ttl'] - time()
                        result.append(answer[0])
        if result:
            print('found in cache')
            return result
        else:
            print('not found in cache')
            return None

    def put_entity(self, parsed_data):
        for answer_section in parsed_data[2:]:
            for answer in answer_section:
                if len(answer['Address']) == 0 or answer['Type'] > 2:
                    continue
                entity = self.storage.get((answer['Name'], answer['Type']))
                if entity is None:
                    self.storage.update(
                        {(answer['Name'], answer['Type']): [(answer, time())]})
                    print('add to cache')
                else:
                    entity.append((answer, time()))
                    print('cache updated')
