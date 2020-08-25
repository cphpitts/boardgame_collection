from django.shortcuts import render, redirect, get_object_or_404
from BoardGame.models import Game, Player, Session
from BoardGame.forms import GameForm, SearchForm, PlayerForm, SessionForm
from django.http import HttpResponse
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django.urls import reverse
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# Display the Home Page
def home(request):
    return render(request, "BoardGame/boardgame_home.html")

# Display the Add Game Form
def addGame(request):
    form = GameForm(request.POST or None)
    # If form was submitted, save the data to the db and redirect to the home page
    if form.is_valid():
        # Check if game is already in the collection (search by name entry)
        query_game = form.cleaned_data['game_name']
        # If the game does not already exists, save the form data
        if not Game.objects.filter(game_name=query_game).exists():
            form.save()
        # If the game already exists, return a URL parameter that will trigger the error message
        else:
            base_url = reverse('bg_viewCollection')
            query_string = urlencode({'exists': '1'})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
        return redirect('bg_viewCollection')
    # Otherwise display the add game form
    else:
        print(form.errors)
        form = GameForm()
        context = {
            'form': form
        }
    return render(request, 'BoardGame/boardgame_add_game.html', context)

# Display the game collection
def viewCollection(request):
    games = Game.objects.all().order_by('game_name')
    # Divide returned game dataset into pages
    page_size = 6 # Set page size to six items
    page = request.GET.get('page', 1)
    paginator = Paginator(games, page_size)
    # Check URL parameter for tag that will indicate a duplicate game was attempted to add to collection
    message_tag = request.GET.get('exists')
    # If the tag exists, set the error message.
    if message_tag == '1':
        message = "This game is already in your collection."
    else:
        message = ""

    # Retrieve current page
    try:
        game_list = paginator.page(page)
    except PageNotAnInteger:
        game_list = paginator.page(1)
    except EmptyPage:
        game_list = paginator.page(paginator.num_pages)

    context = {
        'games': game_list,
        "message": message

    }
    return render(request, "BoardGame/boardgame_collection.html", context)

# View Detail page for a single game
def viewDetail(request, pk):
    pk = int(pk)
    game_detail = get_object_or_404(Game, pk=pk)
    context = {
        'game_detail': game_detail
    }
    return render(request, "BoardGame/boardgame_detail.html", context)

# Edit details of a game
def editDetail(request, pk):
    pk = int(pk)
    game_detail = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game_detail)
        if form.is_valid():
            game_detail.save()
            return redirect('bg_viewDetail', pk=game_detail.pk)
    else:
        form = GameForm(instance=game_detail)
    context = {
        'form': form, #The forms related to the requested game
        'game_detail': game_detail #The actual data related to the requested game
    }
    return render(request, "BoardGame/boardgame_edit.html", context)

# Deletes object from database
def deleteDetail(request, pk):
    g = Game.objects.get(pk=pk)
    g.delete()
    return redirect('bg_viewCollection')

# Request and parse xml from boardgamegeek.com to collect list of hot games
def search(request):
    # Documentation at https://boardgamegeek.com/wiki/page/BGG_XML_API2
    # Request list of hot games from BoardGameGeek.com
    game_type = 'boardgame'
    if request.method == 'POST':
        form = SearchForm(request.POST or None)

        if form.is_valid():
            game_type = form.cleaned_data['game_type']

    query = {
        'type': game_type
    }
    response = requests.get("https://www.boardgamegeek.com/xmlapi2/hot", params=query)
    root = ET.fromstring(response.content)
    games = []
    # Parse through results to collect the game id, title and thumbnail. Add to array
    for bg_item in root.findall('item'):
        bg_id = bg_item.get('id')
        for bg_elem in bg_item.findall('thumbnail'):
            thumbnail = bg_elem.get('value')
        for bg_elem in bg_item.findall('name'):
            title = bg_elem.get('value')
        game_info = {
            "id": bg_id,
            "thumbnail": thumbnail,
            "title": title,

        }
        games.append(game_info)
    form = SearchForm()
    context = {
        "games": games,
        'form': form,
        "game_type": game_type
    }
    return render(request, "BoardGame/boardgame_search.html", context)


# Add a game from the list of hot games to the user's collection
def addHot(request, id):
    message = ""
    id = int(id)
    query = {"id": id}
    # Make a request to the BoardGameGeek API for information regarding a specific game
    response = requests.get("https://www.boardgamegeek.com/xmlapi2/thing", params=query)
    root = ET.fromstring(response.content)
    # Pull out information for the one game. Only object in array
    game = root[0]
    # Check if game already exists in collection. If not, parses the data and adds to the collection
    if not Game.objects.filter(game_name=game.find('name').get('value')).exists():
        # Parse out required information needed for the collection db
        # Placeholder value if data is not present
        game_designer = game_publisher = game_playtime = ""
        # Placeholder value if data is not present
        game_min_players = game_max_players = 0
        game_name = game.find('name').get('value')
        game_image = game.find('image').text
        # Get min and max players & playtime if the values exist
        if game.find('minplayers'):
            game_min_players = game.find('minplayers').get('value')
        if game.find('maxplayers'):
            game_max_players = game.find('maxplayers').get('value')
        if game.find('playingtime'):
            game_playtime = game.find('playingtime').get('value') + " minutes"
        # Cycles through link elements to get publisher and designer
        for link in game.iter('link'):
            # Sets the publisher value if not already set (some games have publisher listed in multiple countries)
            if (link.get('type') == 'boardgamepublisher') and (game_publisher == ""):
                game_publisher = link.get('value')
                continue
            if (link.get('type') == 'rpgpublisher') and (game_publisher == ""):
                game_publisher = link.get('value')
                continue
            # Sets the game designer. Seperates multiple names with comma
            if link.get('type') == 'boardgamedesigner':
                if game_designer == "":
                    game_designer = link.get('value')
                else:
                    game_designer = "{}, {}".format(game_designer, link.get('value'))
                continue
            if (link.get('type') == 'rpgdesigner') and (game_designer == ""):
                if game_designer == "":
                    game_designer = link.get('value')
                else:
                    game_designer = "{}, {}".format(game_designer, link.get('value'))
                continue
        # Create a new game object and assign information based on API results

        new_game = Game()
        new_game.game_name = game_name
        new_game.game_designer = game_designer
        new_game.game_publisher = game_publisher
        new_game.game_min_player = game_min_players
        new_game.game_max_player = game_max_players
        new_game.game_image_path = game_image
        new_game.game_playtime = game_playtime
        new_game.game_expansion = False
        new_game.save()
    # If the game already exists, add a url parameter to flag the error
    else:
        base_url = reverse('bg_viewCollection')
        query_string = urlencode({'exists': '1'})
        url = '{}?{}'.format(base_url, query_string)
        return redirect(url)
    # Redirect to the collection page
    return redirect('bg_viewCollection')

def news(request):
    response = requests.get("https://www.dicetowernews.com/")
    content = BeautifulSoup(response.content, "html.parser")

    storyList = []
    stories = content.find_all('div', class_='node-news-article')
    for story in stories:
        h2_tag = story.h2
        story_link = h2_tag.a.get('href')
        story_title = h2_tag.get_text()
        if story.img:
            story_image = story.img.get('src')
        else:
            story_image = ""

        new_story = {
            # 'h2_tag': h2_tag,
            'story_link': story_link,
            'story_title': story_title,
            'story_image': story_image
        }

        storyList.append(new_story)
    context = {
        'page': storyList,

    }
    return render(request, "BoardGame/boardgame_news.html", context)


def addPlayer(request):
    form = PlayerForm(request.POST or None)
    # If form was submitted, save the data to the db and redirect to the home page
    if form.is_valid():
        form.save()
        return redirect('bg_listPlayer')
    # Otherwise display the add player form
    else:
        print(form.errors)
        form = PlayerForm()
        context = {
            'form': form
        }
    return render(request, 'BoardGame/boardgame_add_player.html', context)


def listPlayer(request):
    players = Player.objects.all().order_by('player_lname')
    context = {
        'players': players,
    }
    return render(request, "BoardGame/boardgame_listplayer.html", context)


def addSession(request):
    form = SessionForm(request.POST or None)
    if form.is_valid():
        newForm = form.save(commit=False)
        newForm.save()
        return redirect('bg_home')
    else:
        form = SessionForm()
        context = {
            'form': form
        }
    return render(request, 'BoardGame/boardgame_addSession.html', context)