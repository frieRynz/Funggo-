import '../models/song.dart';

class MockDatabase {
  static List<Song> songs = [
    Song(
      title: 'Let Down',
      artist: 'Radiohead',
      album: 'OK Computer',
      duration: '4:59',
      lyrics: '... You know, you know where you are with. Floor collapses, floating...',
      imageUrl: 'https://via.placeholder.com/150',
    ),
    Song(
      title: 'Creep',
      artist: 'Radiohead',
      album: 'Pablo Honey',
      duration: '3:56',
      lyrics: 'When you were here before, couldn\'t look you in the eye...',
      imageUrl: 'https://via.placeholder.com/150',
    ),
    Song(
      title: 'No Surprises',
      artist: 'Radiohead',
      album: 'OK Computer',
      duration: '3:48',
      lyrics: 'A heart that\'s full up like a landfill...',
      imageUrl: 'https://via.placeholder.com/150',
    ),
    Song(
      title: 'Karma Police',
      artist: 'Radiohead',
      album: 'OK Computer',
      duration: '4:21',
      lyrics: 'Karma police, arrest this man...',
      imageUrl: 'https://via.placeholder.com/150',
    ),
    Song(
      title: 'Paranoid Android',
      artist: 'Radiohead',
      album: 'OK Computer',
      duration: '6:23',
      lyrics: 'Please could you stop the noise, I\'m trying to get some rest...',
      imageUrl: 'https://via.placeholder.com/150',
    ),
  ];

  static List<Song> searchSongs(String query) {
    if (query.isEmpty) return [];
    
    return songs.where((song) {
      return song.title.toLowerCase().contains(query.toLowerCase()) ||
          song.artist.toLowerCase().contains(query.toLowerCase());
    }).toList();
  }
}