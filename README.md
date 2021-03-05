# **MixedTaper**: Because playlist math is hard
### _A simple way to build play lists for audio cassettes using a Discogs collection_

## **Overview**:
**MixedTaper** is a [Python](https://www.python.org/) app that helps you build track lists from media that has been catalogued in a [Discogs](https://www.discogs.com/) collection. Building track lists and calculating run-time is as easy as clicking and dragging. It is written using Python 3 and requries [PyQt5](https://pypi.org/project/PyQt5/).

## **Basic Setup**:
1) Make sure you have Python 3 setup correctly
2) Install ```PyQt5```
```
pip install PyQt5
```
3) Create an app token ID in the [developer section](https://www.discogs.com/settings/developers) of your discogs account.
4) Clone this repository:
```
git clone https://github.com/mptsolutions/MixedTaper.git
```
5) Enter your ```Discogs``` username and app token ID in the ```simple_discogs.conf``` file:
``` json
{
    "discogs_user_id" : "[DISCOGS_USER_ID]",
    "discogs_user_token" : "[DISCOGS_USER_TOKEN]"
}
```

## **Operation** 
Run the ```mixed_taper.py``` file as any other basic Python script. 
```
D:\PythonProjects\NeverLock> python mixed_taper.py
```
On first run, **MixedTaper** will attempt to retreive all releases in your discogs collection. This can take a while if your collection is large, so be patient. Once the collection has been downloaded, **MixedTaper** will create a local database to minimize the number of times it needs to call the ```Discogs``` service. Note that once created, the local database will need to be manually refreshed to get updates from your collection.  You can perform a manual refresh by clicking anywhere in the ```ARTISTS``` list and pressing ```F5```.  Because of the way the ```Discogs``` service works, the initial download will only include artist and release information - not specific track data. Instead, track lists must be downloaded individually.  To avoid overloading the ```Discogs``` service, track data is only downloaded when it is neecssary. This means that the first timeyou click on a release there will be a slight delay before the track list populates. It also means that **MixedTaper** requires an internet connection during use. However, once track information has been downloaded, it will be stored in the local database so that subsequent lookups do not need to query ```Discogs```. This means that **MixedTaper** will get faster over time and require fewer queries to ```Discogs``` the more you use it.

### Usage
Using **MixedTaper** is simple - just click on an artist to see available releases, then click on a release to see its tracks.  Double-clicking on a track will push it into the ```Side A``` list.  You can then drag the tracks to reorder them, or move them to a different side. Double-click a track to remove it from the side list.  Once you have selected some tracks, click the ```CALCULATE``` button to see the total play time.  The ```SAVE``` button will let you save the track lists as either simple text, or a CSV file.  You can also click the ```CLEAR``` button at the bottom to remove all tracks from both side lists.