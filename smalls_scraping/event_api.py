import json
import logging
import os
import time
import uuid
from random import randrange, uniform
from pyamf import AMF3
from pyamf.flex import messaging
from pyamf.remoting.client import RemotingService

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s')


class EventScraper(object):
    CUTOFF_NUM = 100

    def __init__(self):
        self.gateway_url = os.environ.get('GATEWAY_URL')
        self._refresh_gateway()

    def _refresh_gateway(self):
        # needed to avoid weird unicode decode errors
        self.gateway = RemotingService(self.gateway_url, amf_version=AMF3)
        #self.gateway.setProxy("127.0.0.1:8888")
        self.service = self.gateway.getService("com.smallslive.cfc.smallslive")

    def _date_handler(self, obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def _create_message(self, operation, body):
        self._refresh_gateway()
        return messaging.RemotingMessage(
            body=body,
            operation=operation,
            source='com.smallslive.cfc.smallslive',
            timeToLive=0,
            destination="ColdFusion",
            messageId=str(uuid.uuid4()),
            headers={"DSId": str(uuid.uuid4()), "DSEndpoint": "null"}
        )

    def event_ids_list(self, save=False):
        message = self._create_message('getEventsByType', [51])
        response = self.service.getPeopleByEvent(message)
        events = response.body

        if save:
            with open("events_list.json", "w") as f:
                json.dump(events, f, default=self._date_handler)

        return [event['eventId'] for event in events]

    def _event_request(self, operation, event_id, jsonify=False, as_list=True):
        message = self._create_message(operation, [event_id])
        response = getattr(self.service, operation)(message)
        if as_list:
            obj = list(response.body)
        else:
            obj = response.body[0]
        if jsonify:
            obj = json.dumps(obj, default=self._date_handler)
        return obj

    def event_info(self, event_id, jsonify=False):
        return self._event_request('getEventsDetailByEvent', event_id, jsonify, as_list=False)

    def event_performers(self, event_id, jsonify=False):
        return self._event_request('getPeopleByEvent', event_id, jsonify)

    def event_media(self, event_id, jsonify=False):
        return self._event_request('getMediaByEvent', event_id, jsonify)

    def full_event(self, event_id, jsonify=False):
        event = self.event_info(event_id)
        event['media'] = self.event_media(event_id)
        event['performers'] = self.event_performers(event_id)
        if jsonify:
            event = json.dumps(event, default=self._date_handler)
        return event

    def full_events_list(self):
        event_ids = self.event_ids_list()
        events = []
        for cnt, offset in enumerate(xrange(0, len(event_ids), self.CUTOFF_NUM), start=1):

            segment = event_ids[offset:offset+self.CUTOFF_NUM]

            for idx, id in enumerate(segment, start=1):
                event = self.full_event(id)
                events.append(event)
                time.sleep(uniform(0, 0.6))
                if idx % 100 == 0:
                    print idx

            file_name = "full_events_list_{0}.json".format(cnt)
            with open(file_name, "w") as f:
                print "Writing {0}".format(file_name)
                json.dump(events, f, default=self._date_handler)

if __name__ == '__main__':
    es = EventScraper()
    es.full_events_list()
