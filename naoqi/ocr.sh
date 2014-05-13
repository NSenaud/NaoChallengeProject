#! /usr/bin/env sh

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: ocr.sh                                                            # #
# ########################################################################### #
# # Creation:   2014-04-07                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #

export TESSDATA_PREFIX=/usr/share
tesseract -l fra /tmp/imgOCR.tiff /home/nao/naoqi/output