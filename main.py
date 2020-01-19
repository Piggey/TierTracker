from riotwatcher import RiotWatcher, ApiError
from json import loads, load, dump
from os.path import exists
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime as dt

INTERVAL = 5

def job():
    try:
        watcher = RiotWatcher(key)
        SummonerID = watcher.summoner.by_name(region, name)['id']
        stats = watcher.league.by_summoner(region, SummonerID)[0]
        Tier = stats['tier']
        Rank = stats['rank']
        LeaguePoints = stats['leaguePoints']
        time = dt.datetime.now() + dt.timedelta(minutes=INTERVAL)
        print(f'Current rank: {Tier} {Rank} {LeaguePoints}LP')
        print(f'Next update: {time}')
        fTier = open('tier.txt', 'w').write(f'{Tier} {Rank}')
        fLP = open("leaguePoints.txt", 'w').write(f'{LeaguePoints}LP')

    except ApiError as err:
        if(err.response.status_code == 429):
            print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif(err.response.status_code == 404):
            print('Summoner with that ridiculous name not found.')
        else:
            raise

if(exists('cfg.json')):
    print("Config file detected, loading data from a file.")
    with open('cfg.json') as jsonFile:
        data = load(jsonFile)
        key = data['key']
        region = data['region']
        name = data['name']
    print('Data loaded.')
else:
    regions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'TR1', 'RU']
    name = input('Please enter your Summoner name: ')
    key = input("Paste your Riot API key (get it from https://developer.riotgames.com): ")
    for i, region in enumerate(regions): print(f'[{i}] {region}')
    region = regions[int(input('Select your region: '))]
    print(f'Selected region: {region}')
    cfg = {'key': key, 'region': region, 'name': name}
    with open('cfg.json', 'w') as outfile: dump(cfg, outfile)

sched = BlockingScheduler()
sched.add_job(job, 'interval', minutes=INTERVAL)
job()
sched.start()