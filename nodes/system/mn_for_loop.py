import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_utils import *
from mn_socket_info import *

class mn_ForLoopNode(Node, AnimationNode):
	bl_idname = "mn_ForLoopNode"
	bl_label = "Loop Call"
	
	def getStartLoopNodeItems(self, context):
		startLoopNames = getAttributesFromNodesWithType("mn_ForLoopStartNode", "loopName")
		startLoopNames.sort()
		startLoopNames.reverse()
		startLoopItems = []
		for loopName in startLoopNames:
			startLoopItems.append((loopName, loopName, ""))
		if len(startLoopItems) == 0: startLoopItems.append(("NONE", "NONE", ""))
		return startLoopItems
	def selectedLoopStarterChanged(self, context):
		self.updateSockets(self.getStartNode())
	
	selectedLoop = bpy.props.EnumProperty(items = getStartLoopNodeItems, name = "Loop", update=selectedLoopStarterChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Amount")
		
		self.updateSockets(self.getStartNode())
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if self.selectedLoop == "NONE":
			newNode = layout.operator("node.add_node", text = "New Loop Start", icon = "PLUS")
			newNode.use_transform = True
			newNode.type = "mn_ForLoopStartNode"
		else:
			layout.prop(self, "selectedLoop")
		layout.separator()
		
	def updateSockets(self, startNode):
		forbidCompiling()
		if startNode is None:
			self.resetSockets()
		else:
			connections = getConnectionDictionaries(self)
			self.resetSockets()
			fromListSockets, fromSingleSockets = startNode.getSocketDescriptions()
			
			self.inputs["Amount"].hide = len(fromListSockets) != 0
				
			
			for socket in fromListSockets:
				idName = self.getSocketTypeForListSocket(socket.bl_idname)
				self.inputs.new(idName, socket.customName, socket.identifier + "list")
				self.outputs.new(idName, socket.customName, socket.identifier + "list")
				
			for socket in fromSingleSockets:
				self.inputs.new(socket.bl_idname, socket.customName, socket.identifier)
				self.outputs.new(socket.bl_idname, socket.customName, socket.identifier)
				
			tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def loopRemoved(self):
		self.resetSockets()
		self.inputs["Amount"].hide = True
		
	def resetSockets(self):
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		self.inputs.new("mn_IntegerSocket", "Amount")
		allowCompiling()
			
	def getSocketTypeForListSocket(self, socketType):
		listSocketType = getListSocketType(socketType)
		if listSocketType == None: return "mn_GenericSocket"
		return listSocketType

	def getStartNode(self):
		return getNodeFromTypeWithAttribute("mn_ForLoopStartNode", "loopName", self.selectedLoop)