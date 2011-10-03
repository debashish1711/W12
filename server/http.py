from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log

from vxcontroller import vx

class VxHTTPResource(resource.Resource):
	isLeaf = True
	
	def __init__(self):
		resource.Resource.__init__(self)
	
	# Render / - Index
	def render_Root(self, request):
		request.write("<html><body>")
		request.write("<ul>")
		
		apps = vx.getConnectedApplications()
		
		if len(apps) == 0:
			request.write("No application are connected")
		else:
			# Write each application
			for app in apps:
				request.write("<li>")
				href = '<a href="%(id)s">Application-%(id)s</a>' % {'id':app}
				request.write(href)
				request.write("</li>")
		
		request.write("</ul>")
		request.write("</body></html>")
		request.finish()
		
		# This is the correct way to do this
		return server.NOT_DONE_YET
	
	# Render a connected application
	def render_AvailableApplication(self, request, appid):
		
		# Get WebSocket Handler for this application
		handler = vx.getWebSocketHandlerPath(appid)
		
		# Get html that will be served
		templateFile = open('index.template')
		template = templateFile.read()
		templateFile.close()
		
		# Inject correct handler into html
		html = template % {'id':handler}
		
		# Write html
		request.write(html)
		
		request.finish()
		
		return server.NOT_DONE_YET
		
	# Render an application that is in use
	def render_UnavailableApplication(self, request, clientID):
		return"<html><body>Application is already in use</body></html>"
	
	# Render application that has not connected
	def render_UnknownApplication(self, request, clientID):
			return "<html><body>Unknown Application</body></html>"
	
	# Appropriately render an application
	def render_Application(self, request):
		appid = request.path.split('/', 1)[1]

		if appid in vx.getConnectedApplications():
			
			if vx.applicationIsAvailable(appid):
				return self.render_AvailableApplication(request, appid)
			else:
				return self.render_UnavailableApplication(request, appid)
				
		return self.render_UnknownApplication(request, appid)
	
	# Serve draw.js
	def render_JavaScript(self, request, f):
		# Get JS that will be served
		jsFile = open(f)
		js = jsFile.read()
		jsFile.close()
		request.setHeader("content-type", "application/x-javascript");
		return js
	
	# Hander GET request
	def render_GET(self, request):
		if request.path == '/draw.js' or request.path == '/draw_pr.js' or request.path == '/processing.js' :
			f = request.path[1:]
			return self.render_JavaScript(request, f)
			
		if request.path == '/':
			return self.render_Root(request)
		
		return self.render_Application(request)
