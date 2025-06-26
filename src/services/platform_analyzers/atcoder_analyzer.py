import requests
from bs4 import BeautifulSoup
from .base_analyzer import BaseProfileAnalyzer

class AtcoderAnalyzer(BaseProfileAnalyzer):
    def __init__(self):
        super().__init__()
        self.base_url = "https://atcoder.jp/users"
        self.contests_url = "https://atcoder.jp/contests"
    
    def get_profile(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Get user profile
            profile_response = requests.get(
                f"{self.base_url}/{username}",
                headers=headers,
                timeout=self.timeout
            )
            
            if profile_response.status_code != 200:
                return self.format_error('Invalid AtCoder username')
                
            soup = BeautifulSoup(profile_response.text, 'html.parser')
            
            # Extract profile picture
            profile_img = soup.find('img', class_='avatar')
            profile_picture = profile_img['src'] if profile_img and profile_img.has_attr('src') else ''
            
            # Get table containing user stats
            table = soup.find('table', class_='dl-table')
            if not table:
                return self.format_error('Could not find user statistics')
                
            stats = {}
            for tr in table.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    stats[th.text.strip()] = td.text.strip()
            
            # Extract ratings and ranks
            rating = stats.get('Rating', 'Unrated')
            if rating == '0':
                rating = 'Unrated'
                
            highest_rating = stats.get('Highest Rating', 'Unrated')
            if highest_rating == '0':
                highest_rating = 'Unrated'
                
            rank = stats.get('Rank', 'Unranked')
            if rank == '0':
                rank = 'Unranked'
            
            # Get color based on rating
            color = "Gray"
            rating_int = int(rating) if rating.isdigit() else 0
            if rating_int >= 2800:
                color = "Red"
            elif rating_int >= 2400:
                color = "Orange"
            elif rating_int >= 2000:
                color = "Yellow"
            elif rating_int >= 1600:
                color = "Blue"
            elif rating_int >= 1200:
                color = "Cyan"
            elif rating_int >= 800:
                color = "Green"
            elif rating_int >= 400:
                color = "Brown"
            
            # Get solved count
            problems_solved = 0
            ac_count_span = soup.find('span', class_='user-ac-count')
            if ac_count_span:
                problems_solved = int(ac_count_span.text.strip())
            
            # Get contest history
            contest_history_url = f"{self.base_url}/{username}/history"
            history_response = requests.get(
                contest_history_url,
                headers=headers,
                timeout=self.timeout
            )
            
            recent_contests = []
            if history_response.status_code == 200:
                history_soup = BeautifulSoup(history_response.text, 'html.parser')
                history_table = history_soup.find('table', class_='table')
                
                if history_table:
                    rows = history_table.find_all('tr')[1:]  # Skip header
                    for row in rows[:5]:  # Get last 5 contests
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            contest_date = cols[0].text.strip()
                            contest_name = cols[1].text.strip()
                            rank = cols[2].text.strip()
                            performance = cols[3].text.strip()
                            new_rating = cols[4].text.strip()
                            
                            old_rating = "0"
                            if len(cols) >= 6:
                                rating_change = cols[5].text.strip()
                                old_rating = str(int(new_rating) - int(rating_change) if rating_change.strip('+-').isdigit() and new_rating.isdigit() else 0)
                            
                            recent_contests.append({
                                'name': contest_name,
                                'date': contest_date,
                                'rank': rank,
                                'performance': performance,
                                'old_rating': old_rating,
                                'new_rating': new_rating
                            })
            
            # Get favorite languages
            languages = {}
            submissions_url = f"{self.base_url}/{username}/submissions"
            submissions_response = requests.get(
                submissions_url,
                headers=headers,
                timeout=self.timeout
            )
            
            if submissions_response.status_code == 200:
                submissions_soup = BeautifulSoup(submissions_response.text, 'html.parser')
                submissions_table = submissions_soup.find('table', class_='table')
                
                if submissions_table:
                    rows = submissions_table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 5:  # Make sure we have enough columns
                            lang = cols[3].text.strip()
                            if lang:
                                if lang not in languages:
                                    languages[lang] = 0
                                languages[lang] += 1
            
            # Get top languages
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'username': username,
                'rating': rating,
                'highest_rating': highest_rating,
                'color': color,
                'rank': rank,
                'problems_solved': problems_solved,
                'rated_matches': stats.get('Rated Matches', '0'),
                'class': stats.get('Class', 'Unranked'),
                'affiliation': stats.get('Affiliation', 'None'),
                'country': stats.get('Country/Region', 'Unknown'),
                'birth_year': stats.get('Birth Year', 'Unknown'),
                'last_competed': stats.get('Last Competed', 'Never'),
                'recent_contests': recent_contests,
                'top_languages': [f"{lang} ({count})" for lang, count in top_languages],
                'profile_picture': profile_picture,
                'profile_url': f"https://atcoder.jp/users/{username}"
            }
            
        except requests.Timeout:
            return self.format_error('Request timed out. Please try again.')
        except Exception as e:
            return self.format_error(f'Error fetching AtCoder profile: {str(e)}')