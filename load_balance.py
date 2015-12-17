import re
from functools import partial


class Back_end():
	def __init__(self, Back_end_list, Protocol_avalible, logger):
		
		# Incoming is Protocol://<Usr:Pwd>@Location:Port
		# The list wrap to [(Protocol, Usr, Pwd, Location, Port), ]

		self.Back_ends = []
		self.logger = logger

		URL_par = re.compile("^([^:]+)://([^:]+:[^:]+@)?([^:]+):([^:]+)$")
		Usr_pwd = re.compile("^([^:]+):([^:]+)@$")

		for urls in Back_end_list:
			m = list(URL_par.match(urls).groups())
			if (not m) or (m[0] not in Protocol_avalible) :
				logging.info("This url is unavaliable: %s"%urls)
				continue

			if m[1]:
				m[1] = Usr_pwd.match(m[1]).groups()

			self.Back_ends.append(m)

		# self.Back_ends

	def Get_hash(self, url, back_end_number):
		return hash(str(url))%back_end_number

	def Get_Backend(self, url):
		Back_ser = self.Get_hash(url, len(self.Back_ends))
		remote = self.Back_ends[Back_ser][-2:]
		wrapper = getattr(self, self.Back_ends[Back_ser][0]+'_wrapper')
		return remote, partial(wrapper, auth = self.Back_ends[Back_ser][1]), wrapper

	def http_wrapper(self, src, dst, auth = None):
		source_address = '%s:%s' % src.getpeername()[:2]
		dest_address = '%s:%s' % dst.getpeername()[:2]
		if auth:
			raise BaseException, "This is a future feature"
		else:
			pass

		Buff_size = 1024
		try:
			while True:
				data = src.recv(Buff_size)
				if not data:
					break
				Buff_size = min(Buff_size*2, 65536) if len(data) >= Buff_size else Buff_size
				self.logger.info('%s->%s: %r bytes', source_address, dest_address, len(data))
				dst.sendall(data)
		finally:
			src.close()
			dst.close()

	def https_wrapper(self, src, dst, auth = None):
		source_address = '%s:%s' % src.getpeername()[:2]
		dest_address = '%s:%s' % dst.getpeername()[:2]
		if auth:
			raise BaseException, "This is a future feature"
		else:
			pass
			
		Buff_size = 1024
		try:
			while True:
				data = src.recv(Buff_size)
				if not data:
					break
				Buff_size = min(Buff_size*2, 65536) if len(data) >= Buff_size else Buff_size
				self.logger.info('%s->%s: %r bytes', source_address, dest_address, len(data))
				dst.sendall(data)
		finally:
			src.close()
			dst.close()

	def ss_wrapper(self):
		pass


if __name__ == "__main__":

	B = Back_end([

		"https://127.0.0.1:8087",
		#"http://user:password@127.0.0.1:8080",
		#"ss://encrypt_method:password@1.2.3.4:8388",
		#"cow://method:passwd@1.2.3.4:4321",
		#"https://user:password@127.0.0.1:8080",
		"http://127.0.0.1:8087"

		], ['http', 'https'])

	print B.Get_Backend("uyepwiepwe[wp")
	print B.Get_Backend("uyepwiepwe[wpwjpeajwdpa")
