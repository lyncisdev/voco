import io
import subprocess

# from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types


class Recognizer():
    def recognize(filepath):

        pass


class KaldiRecognizer(Recognizer):
    def recognize(self, filepath):
        result = subprocess.check_output("./kaldi_decode.sh").strip().decode(
            'UTF-8')

        try:

            result = result.split(" ", 1)[1].strip()
        except IndexError as e:
            # this error occurs if Kaldi did not manage to transcribe anything
            result = ""

        return result


class GoogleRecognizer(Recognizer):
    def __init__(self):
        self.client = speech.SpeechClient()

    def recognize(self, filepath):

        # Loads the audio into memory
        with io.open(filepath, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US')

        # Detects speech in the audio file
        response = self.client.recognize(config, audio)

        for result in response.results:
            for alternative in result.alternatives:
                print('Transcript: {}'.format(alternative.transcript))

                return alternative.transcript
        # for result in response.results:

        # print('Transcript: {}'.format(result.alternatives[0].transcript))
