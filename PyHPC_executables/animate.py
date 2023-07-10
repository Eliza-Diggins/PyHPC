"""
======================
Animations in PyHPC
======================
The first step in generating an animation from ``PyHPC`` is to generate the images. This can be done in any of the ways
described in ``PyHPC.PyHPC.PyHPC_Visualization``. Once the image files are produced, one can then use this tool to
stack them together into a final animation. To do so, the command line directive

.. code-block:: commandline

    python3 animate.py -o "<output_directory/ies>" -f "<input_directory/ies>" -r "framerate" -p "<image_pattern>"

The options are as follows:

- ``-o / --outputs``: There are two options to be considered here. If the user specifies a single entity here, it will
  be used as the path for all of the resultant animations, each named via their lowest directory name. For example,

  .. code-block:: commandline

  python3 animate.py -o "/home/images/image_test" -f "/home/images_1" "/home/images_2"

  will produce 2 files: ``/home/images/image_test/images_1.mp4``, and ``/home/images/image_test/images_2.mp4``. If instead, a list
  of outputs is provided which is the same length as the list of files, then each file will be directly mapped to that
  output scheme for generating the outputs.

- ``f / --files``: These are the directories which should be used to generate the animation. The ``.png`` files contained
  within the directories are converted into a movie.

- ``p / --pattern``: The pattern to use for image file detection. This should be decided by the user's naming conventions.
"""
import os
import pathlib as pt
import sys

# adding the system path to allow us to import the important modules
sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
import argparse
from PyHPC.PyHPC_Core.log import configure_logging
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Utils.text_display_utilities import PrintRetainer, TerminalString, print_title
import pathlib as pt
from colorama import Fore, Style
import warnings
import logging
from time import sleep
from tqdm import tqdm
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyCS_Tools"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)
printer = PrintRetainer()
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Fixed Variables -#
ffmpeg_command = CONFIG["System"]["Modules"]["ffmpeg_exec_func"]
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ----------------------------------------------------- Main ------------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    configure_logging(_filename)
    # Parsing Arguments
    ########################################################################################################################
    parser = argparse.ArgumentParser()  # setting up the command line argument parser
    parser.add_argument("-f",'--files', required = True,nargs='+', help='The directories from which to pull the frames.')
    parser.add_argument("-o",'--outputs', required=True, nargs='+', help='The directory or file names to assign to the movies.')
    parser.add_argument("-r", "--framerate", default=20, type=int, help="The frame rate of the output movies.")
    parser.add_argument("-p","--pattern",type=str,default="Image_*.png",help="The naming convention for the image files.")
    args = parser.parse_args()

    # Setup Tasks
    ########################################################################################################################
    term_string = TerminalString()  # Loading a terminal string
    print_title(func=printer.print)  # Printing the title
    printer.print(term_string.str_in_grid(""))
    printer.print(
        term_string.str_in_grid(Fore.BLUE + "Image Generation Software" + Style.RESET_ALL, alignment="center"))
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.h + "\n")

    if CONFIG["System"]["Modules"]["ffmpeg_env_script"] != "":
        os.system(CONFIG["System"]["Modules"]["ffmpeg_env_script"])

    for i in tqdm(range(100), desc="[PyHPC]:   | Loading..." ,bar_format="{desc}: {percentage:3.0f}%|{bar}|",
                  ncols=term_string.dim_alt[0]):
        sleep(0.01)

    input("[PyHPC]:   | Press any key to continue...")


    #  Sanity Check
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("[PyHPC]:   (DEBUG) | Checking user inputs for sanity checks...")
    assert len(args.files) > 0, "You must specify a non-zero number of directories."
    assert len(args.outputs) > 0, "You must specify a non-zero number of output paths"
    assert len(args.outputs) == 1 or len(args.outputs) == len(
        args.files), "Size mismatch: outputs must be length 1 or same size as files."

    if len(args.outputs) == 1:
        args.outputs = args.outputs * len(args.files)

    out_ids = []
    for fid, directory in enumerate(args.files):
        if not os.path.exists(directory):
            printer.print(f"[PyHPC]:   (ERROR) | The directory {directory} doesn't exist.")
            out_ids += [fid]

    args.outputs, args.files = [j for i, j in enumerate(args.outputs) if i not in out_ids], [j for i, j in
                                                                                              enumerate(args.files) if
                                                                                              i not in out_ids]

    assert len(args.outputs), "Failed to find any remaining valid outputs."
    assert len(args.files), "Failed to find any remaining file outputs."

    printer.print(term_string.h)
    for direct in args.files:
        printer.print("\tFound "+Fore.GREEN+f"{direct}"+Fore.CYAN+f"\t\t[{len(os.listdir(direct))}] files"+Style.RESET_ALL)
    printer.print(f"Located {len(args.files)} directories for video generation...\n")
    input("[PyHPC]:   | Press any key to continue...")
    # Attempting to generate movies
    ####################################################################################################################
    printer.print(term_string.h)
    printer.print(term_string.str_in_grid(Fore.CYAN+"GENERATING ANIMATIONS..."+Style.RESET_ALL,alignment="center"))
    printer.print(term_string.h)
    for animation_directory, output_directory in tqdm(zip(args.files,args.outputs)):
        #  Managing the base output location / other checks
        # -------------------------------------------------------------------------------------------------------------#
        _valid_files = [file for file in os.listdir(animation_directory) if ".png" in file]

        if not len(_valid_files):
            tqdm.write(f"[PyHPC]:   (WARNING) | Failed to find valid .png files in {animation_directory}")
            continue

        #- Dealing with the output directory -#
        if os.path.isdir(animation_directory):
            output_path = os.path.join(output_directory,pt.Path(animation_directory).name+".mp4")
        else:
            output_path = animation_directory

        pt.Path(output_path).parents[0].mkdir(exist_ok=True,parents=True)


        # - grabbing the image names -#
        image_style = str(os.path.join(animation_directory, args.pattern))
        # Creating the Movie
        ############################################################################################################
        os.system(ffmpeg_command % (args.framerate, image_style, output_path))
    print("[PyHPC]    [INFO]: Finished.")
