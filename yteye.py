def display_header():
    header = """
\033[93m@@@ @@@  @@@@@@@       @@@@@@@@  @@@ @@@  @@@@@@@@\033[0m
\033[93m@@@ @@@  @@@@@@@       @@@@@@@@  @@@ @@@  @@@@@@@@\033[0m
\033[92m@@! !@@    @@!         @@!       @@! !@@  @@!\033[0m
\033[91m!@! @!!    !@!    @!@  !@!       !@! @!!  !@!\033[0m
\033[96m !@!@!     @!!    !@!  @!!!:!     !@!@!   @!!!:!\033[0m
\033[95m  @!!!     !!!    :!:  !!!!!:      @!!!   !!!!!:\033[0m
\033[94m  !!:      !!:         !!:         !!:    !!:\033[0m
\033[93m  :!:      :!:    :!:  :!:         :!:    :!:\033[0m
\033[97m   ::       ::     ::   :: ::::     ::     :: ::::\033[0m
\033[96m   :        :     ::   : :: ::      :     : :: ::\033[0m
\033[37m----------------------------------------------------------\033[0m
\033[92m    ➤ Tool For OSINT;\033[0m            ➤ \033[91mVersion: 1.0;\033[0m
\033[92m    ➤ Author: @CyberWo9f;\033[0m    ➤ An eye on YT;chat✅;\033[0m
\033[37m----------------------------------------------------------\033[0m
    """
    print(header)

def link_to_generate_ids():
    response = input("➤ Do you want to generate stream ID's? (Y/N): ").strip().upper()
    if response == 'Y':
        # Link to the Python file for generating live_stream_ids (replace 'generate_live_ids.py' with the actual filename)
        import subprocess
        subprocess.run(["python", "link.py"])
    elif response == 'N':
        # Link to another Python file for handling when live_stream_ids are not generated (replace 'no_generate_live_ids.py' with the actual filename)
        import subprocess
        subprocess.run(["python", "yteye6.py"])
    else:
        print("[!]Invalid input. Please enter Y or N.")

# Call the function to display the header
display_header()

# Call the function to link to Python files based on user input
link_to_generate_ids()
