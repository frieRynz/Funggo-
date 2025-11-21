class Song {
  final String title;
  final String artist;
  final String album;
  final String duration;
  final String lyrics;
  final String? imageUrl;

  Song({
    required this.title,
    required this.artist,
    required this.album,
    required this.duration,
    required this.lyrics,
    this.imageUrl,
  });

  factory Song.fromJson(Map<String, dynamic> json) {
    return Song(
      // Use '??' to provide default values if a field is missing in the DB
      title: json['title'] ?? 'Unknown Title',
      artist: json['artist'] ?? 'Unknown Artist',
      album: json['album'] ?? 'Unknown Album',
      duration: json['duration'] ?? 'N/A', 
      lyrics: json['lyrics'] ?? '',
      imageUrl: null, // Covers camelCase or snake_case
    );
  }

}