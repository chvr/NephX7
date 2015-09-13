# Rigathon startup script
# - Add lines below to userSetup.py in /scripts of maya settings directory
#   (create userSetup.py if it doesn't exist)

import maya.cmds as cmds

def cnx_rigathon():
	try:
		global cnx_rigathon_module
		cnx_rigathon_module
	except NameError:
		# NOTE: Change the following to point to Rigathon directory
		_RIGATHON_DIR = 'C:/$_Chyros/GameDev/Workspace/Python/rigathon'

		if _RIGATHON_DIR not in sys.path:
			sys.path.append(_RIGATHON_DIR)

		from cnx_rigathon import Rigathon
		cnx_rigathon_module = Rigathon(_RIGATHON_DIR)

cmds.scriptJob(event = ['NewSceneOpened', cnx_rigathon])
