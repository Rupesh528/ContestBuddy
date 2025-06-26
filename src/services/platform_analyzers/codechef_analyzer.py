import requests
from bs4 import BeautifulSoup
from .base_analyzer import BaseProfileAnalyzer

class CodechefAnalyzer(BaseProfileAnalyzer):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.codechef.com/users"
    
    def get_profile(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(
                f"{self.base_url}/{username}",
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract profile picture
            profile_pic = ''
            img_tag = soup.select_one('.user-details-container img')
            if img_tag and img_tag.has_attr('src'):
                profile_pic = img_tag['src']
                if not profile_pic.startswith(('http://', 'https://')):
                    profile_pic = f"https://www.codechef.com{profile_pic}"
            
            # Extract Rating and Ranking
            rating = soup.find("div", class_="rating-number")
            rating = rating.text.strip() if rating else "Unrated"
            
            # Extract Division
            division_tag = soup.find("div", class_="rating-header")
            division = division_tag.find_all("div")[1].text.strip("()") if division_tag and len(division_tag.find_all("div")) > 1 else "Unknown"
            
            # Extract Stars
            stars = len(soup.find_all("span", class_="rating-star"))
            
            # Extract Highest Rating
            highest_rating_tag = soup.find("small")
            highest_rating = highest_rating_tag.text.strip("()").split()[-1] if highest_rating_tag else "Unrated"
            
            # Get global and country ranks
            global_rank = "Unranked"
            country_rank = "Unranked"
            
            global_rank_tag = soup.find("a", href="/ratings/all")
            if global_rank_tag and global_rank_tag.find("strong"):
                global_rank = global_rank_tag.find("strong").text.strip()
            
            country_rank_tag = soup.find("a", href=lambda x: x and "filterBy=Country" in x)
            if country_rank_tag and country_rank_tag.find("strong"):
                country_rank = country_rank_tag.find("strong").text.strip()
            
            # Extract country
            country = "Unknown"
            country_div = soup.find("div", class_="user-country-name")
            if country_div:
                country = country_div.text.strip()
            
            # Get recent contest history
            contest_history = []
            contest_table = soup.find('table', class_='rating-table')
            if contest_table:
                rows = contest_table.find_all('tr')[1:]  # Skip header
                for row in rows[:5]:  # Get last 5 contests
                    cols = row.find_all('td')
                    if len(cols) >= 5:  # Ensure we have enough columns
                        contest_name = cols[0].text.strip()
                        contest_date = cols[1].text.strip()
                        contest_rank = cols[2].text.strip()
                        old_rating = cols[3].text.strip()
                        new_rating = cols[4].text.strip()
                        change = int(new_rating) - int(old_rating) if new_rating.isdigit() and old_rating.isdigit() else 0
                        
                        if contest_name and contest_rank:
                            # Clean up the rank text
                            rank = ''.join(filter(str.isdigit, contest_rank))
                            contest_history.append({
                                'name': contest_name,
                                'date': contest_date,
                                'rank': f"#{rank}" if rank else 'Unranked',
                                'old_rating': old_rating,
                                'new_rating': new_rating,
                                'change': change
                            })
            
            # Get fully, partially solved problems count
            fully_solved = 0
            partially_solved = 0
            
            problem_stats = soup.find('div', class_='content')
            if problem_stats:
                fully_section = problem_stats.find('h5', string=lambda t: t and 'Fully Solved' in t)
                partially_section = problem_stats.find('h5', string=lambda t: t and 'Partially Solved' in t)
                
                if fully_section:
                    next_div = fully_section.find_next('div')
                    if next_div:
                        fully_solved = len(next_div.find_all('a'))
                
                if partially_section:
                    next_div = partially_section.find_next('div')
                    if next_div:
                        partially_solved = len(next_div.find_all('a'))
            
            # Get activity data
            activity_data = {}
            try:
                # Find the script with activity data
                for script in soup.find_all('script'):
                    if script.string and 'window.activity' in script.string:
                        script_content = script.string
                        activity_start = script_content.find('window.activity')
                        if activity_start != -1:
                            # Find the JSON part for activity
                            activity_json_start = script_content.find('{', activity_start)
                            activity_json_end = script_content.find('};', activity_json_start)
                            if activity_json_start != -1 and activity_json_end != -1:
                                activity_json = script_content[activity_json_start:activity_json_end+1]
                                # Extract the activity counts (simplified approach)
                                try:
                                    import re
                                    counts = re.findall(r'"([^"]+)":\s*(\d+)', activity_json)
                                    activity_data = {month: int(count) for month, count in counts}
                                except:
                                    pass
            except:
                pass
            
            # Get badges
            badges = []
            badges_section = soup.find('span', string=lambda t: t and 'Badges' in t)
            if badges_section:
                badge_items = badges_section.find_parent('div').find_all('li') if badges_section.find_parent('div') else []
                for badge in badge_items:
                    badge_text = badge.text.strip() if badge else ""
                    if badge_text:
                        badges.append(badge_text)
            
            return {
                'username': username,
                'rating': rating,
                'highest_rating': highest_rating,
                'division': division,
                'stars': f"{stars} ★" if stars > 0 else "0",
                'global_rank': f"#{global_rank}" if global_rank != 'Unranked' else global_rank,
                'country_rank': f"#{country_rank}" if country_rank != 'Unranked' else country_rank,
                'country': country,
                'problems_fully_solved': fully_solved,
                'problems_partially_solved': partially_solved,
                'total_problems_solved': fully_solved + partially_solved,
                'recent_contests': contest_history,
                'profile_picture': profile_pic,
                'monthly_activity': activity_data,
                'badges': badges,
                'profile_url': f"https://www.codechef.com/users/{username}"
            }
            
        except requests.Timeout:
            return self.format_error('Request timed out. Please try again.')
        except requests.exceptions.RequestException as e:
            return self.format_error(f'Failed to fetch details: {str(e)}')
        except Exception as e:
            return self.format_error(f'An error occurred: {str(e)}')