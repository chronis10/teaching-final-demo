import os
import threading

import tensorflow as tf
import tensorflow_addons as tfa
import numpy as np
import time

from base.node import TEACHINGNode
from base.communication.packet import DataPacket
from .base_module import LearningModule


class RLModule(LearningModule):

    FED_TOPIC='rlmodule'

    def __init__(self):
        super(RLModule, self).__init__()
        self._periodic_sender = None
        self._aggregator = None
        self._build()
        #'Ego_VehicleSpeed','Ego_YawRate','Ego_Acceleration_y','Ego_Acceleration_x','Vehicle.Heading','TOF_Distance_x'
        self.normalize_mask = np.array([101,50,10,15,600,500])
    
    @TEACHINGNode(produce=True, consume=True)
    def __call__(self, input_fn):
        for msg in input_fn:
            self._aggregator.aggregate(msg)
            if self._aggregator.is_ready():
                profile = self._model.predict(np.asarray([self._aggregator._batch_data])/self.normalize_mask)
                self._aggregator.clean()
                final_value = float(np.argmax(profile[0]))
                
                yield DataPacket(
                    topic='prediction.driving_profile.value',
                    body={'driving_profile': final_value }
                )

    def _build(self):
        super(RLModule, self)._build()        
        self._model = tf.keras.models.load_model(self._model_path, custom_objects={'AdamW':tfa.optimizers.AdamW})
        self._model.summary()
        self._aggregator = Aggregator()
        if self.federated:
            self._periodic_sender = periodic_send_model(self)


class Aggregator():

    def __init__(self):
        self._namespaces = ['Ego_VehicleSpeed','Ego_YawRate','Ego_Acceleration_y','Ego_Acceleration_x','Vehicle.Heading','TOF_Distance_x']
        self._batch_data = [None]*len(self._namespaces)
        
    def aggregate(self,msg):
        if type(msg.body) == list:
            msg.body = msg.body[0]

        msg_keys = msg.body.keys()              
        for vkey in msg_keys:
            if vkey in self._namespaces:
                position =  self._namespaces.index(vkey)
                self._batch_data[position] = msg.body[vkey]
        

    def is_ready(self):        
        for value in self._batch_data:
            if value is None:
                return False
        return True

    def clean(self):
        self._batch_data = [None]*len(self._namespaces)


def periodic_send_model(lm):
    def aux_fn():
        send_every_t = int(os.getenv('SEND_MODEL_INTERVAL', '5'))
        while True:
            time.sleep(send_every_t)
            lm._train()
            lm._client.send_model = {'model': tf.keras.models.clone_model(lm._model), 'metadata': {}}
    
    periodic_sender = threading.Thread(target=aux_fn)
    periodic_sender.start()
    return periodic_sender