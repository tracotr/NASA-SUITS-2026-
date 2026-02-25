from tts_engine import TTSEngine

def main():
    '''
    Simple input terminal for testing TTS engine voices
    '''
    tts = TTSEngine()
    quit_command = ['quit', 'q']
    clear_command = ['clear', 'c']

    try:
        print("---- TTS Testing Terminal ----")
        print("Command: Function")
        print(f"{quit_command}: Close out of the program")
        print(f"{clear_command}: Clear the current queue of text and speech")

        while True:
            user_input = input("Say: ").strip()

            # quit the program
            if(user_input.lower() in ['quit', 'q']):
                break

            # clear the current queue of speech
            if(user_input.lower() in ['clear', 'c']):
                tts.stop()
                continue

            tts.speak(user_input)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")

if __name__ == "__main__":
    main()