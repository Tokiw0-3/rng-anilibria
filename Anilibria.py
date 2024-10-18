import requests
from bs4 import BeautifulSoup
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Fetch anime from anilibria.tv
def fetch_anilibria_tv_anime():
    alphabet_url = 'https://www.anilibria.tv/pages/alphabet.php'
    anime_list = []

    try:
        response = requests.get(alphabet_url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        anime_elements = soup.select('td.goodcell a')  # Find all links within goodcell <td>
        
        for elem in anime_elements:
            anime_url = f"https://www.anilibria.tv{elem['href']}"  # Construct full URL
            anime_title = elem.find('span', class_='schedule-runame').text  # Get the title
            anime_list.append((anime_title, anime_url))  # Store title and URL as a tuple

        # Randomly select a few anime
        recommended_anime = random.sample(anime_list, min(5, len(anime_list)))
        anime_details = []

        # Fetch details for each selected anime
        for anime in recommended_anime:
            anime_title = anime[0]
            anime_url = anime[1]
            description, image_url = fetch_anime_details_tv(anime_url)
            anime_details.append({
                'title': anime_title,
                'description': description,
                'url': anime_url,
                'image_url': image_url,
                'site': 'tv'  # Mark the source site
            })

        return anime_details

    except requests.RequestException as e:
        print(f"Error fetching anime list: {e}")
        return []

def fetch_anime_details_tv(anime_url):
    try:
        response = requests.get(anime_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract description
        description_elem = soup.find('p', class_='detail-description')
        description = description_elem.text.strip() if description_elem else "Description not available."

        # Extract image URL
        image_elem = soup.find('img', id='adminPoster')
        image_url = f"https://www.anilibria.tv{image_elem['src']}" if image_elem else None

        return description, image_url

    except requests.RequestException as e:
        print(f"Error fetching anime details: {e}")
        return "Error fetching details.", None


# Fetch random anime from anilibria.best
def fetch_anilibria_best_anime():
    random_page = random.randint(1, 222)
    url = f'https://anilibria.best/page/{random_page}/'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        anime_elements = soup.select('.kino-item')  # Select elements with class kino-item

        if anime_elements:
            random_anime = random.choice(anime_elements)
            anime_title = random_anime.select_one('.kino-title').text.strip()
            anime_desc = random_anime.select_one('.kino-desc').text.strip()
            anime_url = random_anime.find('a')['href']
            image_url = fetch_anime_image_best(anime_url)

            return {
                'title': anime_title,
                'description': anime_desc,
                'url': anime_url,
                'image_url': image_url,
                'site': 'best'  # Mark the source site
            }

    except requests.RequestException as e:
        print(f"Error fetching anime from page {random_page}: {e}")

    return None

def fetch_anime_image_best(anime_url):
    try:
        response = requests.get(anime_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        image_elem = soup.select_one('.highslide')
        if image_elem and 'href' in image_elem.attrs:
            return image_elem['href']
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching image: {e}")
        return None


# Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    anime_details = []
    if request.method == 'POST':
        number_of_anime = int(request.form.get('number_of_anime', 1))

        for _ in range(number_of_anime):
            selected_site = random.choice(['tv', 'best'])

            if selected_site == 'tv':
                anime_from_tv = fetch_anilibria_tv_anime()
                if anime_from_tv:
                    anime_details.append(random.choice(anime_from_tv))  # Pick a random anime from tv
            else:
                anime_from_best = fetch_anilibria_best_anime()
                if anime_from_best:
                    anime_details.append(anime_from_best)

        return render_template('index.html', anime_details=anime_details)

    return render_template('index.html', anime_details=[])

if __name__ == "__main__":
    app.run(debug=True)
