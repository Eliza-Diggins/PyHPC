"""
This is a micro-executable which allows us to produce a single plot.
"""
import argparse
import logging
import os
import pathlib as pt
import warnings
import sys
sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import yaml
import PyHPC.PyHPC_Visualization.uplots as uplots
from PyHPC.PyHPC_Visualization.plot import PlotDirective,generate_image
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.log import configure_logging
from PyHPC.PyHPC_Core.errors import PyHPC_Error

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_Executable"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

if __name__ == '__main__':
    #  Debugging intro
    # ----------------------------------------------------------------------------------------------------------------- #
    configure_logging(_filename)
    modlog.debug("Generating images.")
    print("[PyHPC]:   (INFO) | Generating image.")
    #  Loading command line arguments
    # ----------------------------------------------------------------------------------------------------------------- #
    parser = argparse.ArgumentParser()

    parser.add_argument("pdir",help="The path to the correct p-directive",type=str)
    parser.add_argument("-o","--output",help="The output path corresponding to the p-dir.",default=os.path.join(os.getcwd(),"out.png"))

    args,unknown = parser.parse_known_args()
    additional_kwargs = {unknown[i].replace("--",""):unknown[i+1] for i in range(0,len(unknown),2)}

    print(additional_kwargs)
    #  Generating the image.
    # ----------------------------------------------------------------------------------------------------------------- #
    try:
        plot_directive = PlotDirective(args.pdir)
    except FileNotFoundError:
        print("[PyHPC]:   (ERROR) | Failed to locate plot directive at %s. Exiting..."%args.pdir)
        exit()
    except yaml.YAMLError:
        print("[PyHPC]:   (ERROR) | Pdir was not correctly formatted. Exiting...")
        exit()

    print("[PyHPC]:   (INFO) | Loaded %s from file at %s"%(plot_directive,args.pdir))

    print("[PyHPC]:   (INFO) | Generating image...")
    try:
        dat = generate_image(plot_directive,**additional_kwargs)
    except Exception:
        modlog.exception("Failed to plot image.")
        print("[PyHPC]:   (ERROR) | FAILED. Exiting...")
        exit()

    if dat[0] == "normal":
        print("[PyHPC]:   (INFO) | PATH=STANDARD")
        print("[PyHPC]:   (INFO) | Finished.")
        print("[PyHPC]:   (INFO) | Saving to file at %s."%args.output)
        if not os.path.exists(pt.Path(args.output).parents[0]):
            pt.Path(args.output).parents[0].mkdir(parents=True)
        plot_directive.figure.savefig(args.output)

        print("[PyHPC]:   (INFO) | Finished.")
    elif dat[0] == "volume_render":
        print("[PyHPC]:   (INFO) | PATH=VOLUME_RENDER")
        print("[PyHPC]:   (INFO) | Finished.")
        print("[PyHPC]:   (INFO) | Saving to file at %s." % args.output)
        if not os.path.exists(pt.Path(args.output).parents[0]):
            pt.Path(args.output).parents[0].mkdir(parents=True)
        dat[1].render()
        dat[1].save(args.output,sigma_clip=3.0)

        print("[PyHPC]:   (INFO) | Finished.")
    else:
        raise ValueError("Unknown status from generate_image.")

    exit()


