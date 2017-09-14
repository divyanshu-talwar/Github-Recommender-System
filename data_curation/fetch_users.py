import requests, json

response = requests.get('https://api.github.com/users?since=0&page=1&per_page=100&client_id=####&client_secret=####')

file = open('users1.dat', 'w')

count = 0

while(response.ok):
	print(count+1)
	link = response.headers.get('link',None)
	item = json.loads(response.text or response.content)
	file.write(str(item) + "\n")
	if(count == 100): 
		print("ratelimit left : ")
		print(response.headers.get("x-ratelimit-remaining", None))
		break
	if(link is not None):
		count += 1
		link = link.split(">")[0][1:]
		response = requests.get(link)

print(response)
file.close()