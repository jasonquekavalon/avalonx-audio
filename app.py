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

@socketio.on('connect', namespace='/test')
def test_connect():
    session['audio'] = []
    emit('my_response',
                    {'data': 'I\'m connected!'})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate

@socketio.on('audio', namespace='/test')
def handle_my_custom_event(audio):
    values = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['audio'] += values

@socketio.on('disconnect_request', namespace='/test')
def first_disconnect():
    emit('my_response',
        {'data': 'Detecting language...'})

@socketio.on('test_disconnect', namespace='/test')
def test_disconnect():
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
        from google.cloud import speech_v1p1beta1 as speech
        client = speech.SpeechClient()

        first_lang = 'en-US'  #english
        second_lang = 'es'  #spanish
        third_lang = 'zh' #chinese
        fourth_lang = 'pl-PL' #polish
        fifth_lang = 'de-DE' #german
        sixth_lang = 'sv-SE' #swedish
        seventh_lang = 'nb-NO' #norwegian
        eighth_lang = 'it-IT' #italian

        language = {'en-us': 'English', 'es': 'Spanish', 'cmn-hans-cn': 'Chinese', 'pl-PL': 'Polish', 'de-de': 'German', 'sv-SE': 'Swedish', 'nb-no': 'Norwegian', 'it-it': 'Italian'}

        audio = speech.types.RecognitionAudio(content=f.getvalue())
        config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        #    sample_rate_hertz=sampleRate,
            language_code=first_lang,
            alternative_language_codes=[second_lang,third_lang,fourth_lang])

        response = client.recognize(config, audio)

        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            confidence = float('{}'.format(alternative.confidence))
            transcript = '{}'.format(alternative.transcript)
            language_code =  str(result.language_code)
            if confidence > 0.8:
                confidence = int(confidence *100)
                languages = language[language_code]
                print('language : ' + languages)
                emit('my_response',
                    {'data': 'I am %s percent confident that you are speaking %s \n' %(confidence,languages)})
            else : 
                config = speech.types.RecognitionConfig(
                encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            #    sample_rate_hertz=sampleRate,
                language_code=fifth_lang,
                alternative_language_codes=[sixth_lang,seventh_lang,eighth_lang])

                response = client.recognize(config, audio)

                for i, result in enumerate(response.results):
                    alternative = result.alternatives[0]
                    confidence = float('{}'.format(alternative.confidence))
                    transcript = '{}'.format(alternative.transcript)
                    language_code =  str(result.language_code)
                    if confidence > 0.8:
                        confidence = int(confidence *100)
                        languages = language[language_code]
                        print('language : ' + languages)
                        emit('my_response',
                            {'data': 'I am %s percent confident that you are speaking %s \n' %(confidence,languages)})
                    else:
                        emit('my_response',
                            {'data': 'Sorry we could not recognise that language. Try speaking clearly \n'})

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