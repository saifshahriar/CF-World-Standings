import requests
from bs4 import BeautifulSoup
from login import login, get_csrf

# Global Variables #
cf_url = "https://codeforces.com"
lists_url = "https://codeforces.com/lists"
new_list_url = "https://codeforces.com/lists/new"
edit_list_url = "https://codeforces.com/data/lists"

def get_page(session, url):
	request = session.get(url)
	plain = request.text
	page = BeautifulSoup(plain, "html.parser")
	return page

def get_lists_table(session, url):
	page = get_page(session, url)
	table_div = page.find('div', {'class': 'datatable'})
	table = table_div.find('table')
	table_rows = table.find_all('tr')
	return table_rows

def get_lists_urls(table):
	urls = {}
	for row in table:
		if row.find('a'):
			country = row.find('a').text
			country_list_url = cf_url + row.find('a')['href']
			urls[country] = country_list_url
	return urls

def create_lists(session, countries_dict):
	table = get_lists_table(session, lists_url)
	lists_urls = get_lists_urls(table)
	countries_list = []
	for country in countries_dict:
		if country not in lists_urls and len(countries_dict[country]) >= 5:
			request = session.get(new_list_url)
			csrf = get_csrf(request)
			n = session.post(new_list_url, data={ 'csrf_token': csrf, 'action': 'saveList', 'englishName': country, '_tta': 90 })
			countries_list.append(country)
			print(f"\tList of {country} created! {n}")

def clear_lists(session):
	table = get_lists_table(session, lists_url)
	lists_urls = get_lists_urls(table)
	for country in lists_urls:
		url = lists_urls[country]
		request = session.get(url)
		csrf = get_csrf(request)
		table = get_lists_table(session, url)
		if len(table) < 1000:
			print(f'\tList of {country} skipped!')
			continue
		list_id = get_page(session, url).find('a', {'class': 'delete-user-list-link'})["data-userlistid"]
		for row in table:
			try:
				user_id = row.findAll('td')[-1]["data-userid"]
				params = {'action': 'deleteMember', 'listId': list_id, 'userId': user_id, 'csrf_token': csrf }
				session.post(edit_list_url, data=params)
			except:
				pass
		print(f'\tList of {country} emptied!')

def populate_list(session, handles, list_url):
	request = session.get(list_url)
	csrf = get_csrf(request)
	params = {'csrf_token': csrf, 'action': 'addMembers', 'handlesToAdd': handles }
	session.post(list_url, data=params)

def populate_lists(session, countries_dict):
	table = get_lists_table(session, lists_url)
	lists_urls = get_lists_urls(table)
	for country in lists_urls:
		if country in countries_dict:
			handles = []
			for user in countries_dict[country][:1000]: handles.append(user[2])
			handles = " ".join(handles)
			populate_list(session, handles, lists_urls[country])
			print(f"\tList of {country} populated!")

if __name__ == "__main__":
	login()