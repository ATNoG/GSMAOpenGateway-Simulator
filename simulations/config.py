# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 19:37:09
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 22:36:07
import logging
import sys
from pathlib import Path

# Configure Loggging
root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)

# Configure Sys Path for Imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
