#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response, session
from flask_socketio import SocketIO, emit, disconnect
import io
import json
import scipy.io.wavfile
import numpy as np
from collections import OrderedDict

from google.cloud import speech_v1p1beta1 as speech

className = 'NONE'
app = Flask(__name__)
socketio = SocketIO(app, binary=True, async_mode='eventlet')


@app.route('/healthz', methods=['GET'])
def health_check():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

#@socketio.on('disconnect_request', namespace='/test')
#def disconnect_request():
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': 'Disconnected!', 'count': session['receive_count']})
# s    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    session['audio'] = []
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    # send some message to front
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': "sampleRate : %s" % sampleRate, 'count': session['receive_count'] })

@socketio.on('audio', namespace='/test')
def handle_my_custom_event(audio):
    values = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['audio'] += values

@socketio.on('disconnect_request', namespace='/test')
def test_disconnect():
    print('disconnecting')
    emit('my_response', {'data': 'Thinking...', 'count': 0})
    sample_rate = session['sample_rate']
    my_audio = np.array(session['audio'], np.float32)
    sindata = np.sin(my_audio)
    scaled = np.round(32767*sindata)
    newdata = scaled.astype(np.int16)
    with io.BytesIO() as f:
        scipy.io.wavfile.write(f, sample_rate, newdata)

        session['audio'] = []

        """Transcribe the given audio file using an enhanced model."""
        # [START speech_transcribe_enhanced_model_beta]
        client = speech.SpeechClient()

        first_lang = 'en-US'
        second_lang = 'es'
        third_lang = 'yue-Hant-HK'
        fourth_lang = 'pl-PL'

        print('transcribing')
        audio = speech.types.RecognitionAudio(content=f.getvalue())
        config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code=first_lang,
            alternative_language_codes=[second_lang,third_lang,fourth_lang])
        print("running recognize")
        response = client.recognize(config, audio, retry=None, timeout=60)
        print("getting results")
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            print('{}'.format(alternative.transcript))
            print(response.results)
            response = '{}'.format(alternative.transcript)
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response', {'data': response, 'count': session['receive_count'] })
        print(response)
    disconnect()

@app.route('/speech_recognition', methods=['GET'])
def game3():
    return render_template('speech_recognition.html')

def initClass(name):
    global className, count
    className = name


if __name__ == '__main__':
    initClass('NONE')
    socketio.run(app, debug=True)