import 'package:flutter/material.dart';
import '../models/song.dart';
import '../screens/song_detail_page.dart' as detail;

class SongCard extends StatelessWidget {
  final Song song;
  final String searchQuery;

  const SongCard({Key? key, required this.song, this.searchQuery = ''})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => detail.SongDetailPage(song: song),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Album art placeholder
              Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.music_note, color: Colors.grey, size: 32),
              ),
              const SizedBox(width: 16),
              // Song info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      song.title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Artist: ${song.artist}',
                      style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                    ),
                    const SizedBox(height: 8),
                    _buildLyricsPreview(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLyricsPreview() {
    if (searchQuery.isEmpty) {
      return Text(
        song.lyrics,
        style: TextStyle(fontSize: 13, color: Colors.grey[600]),
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      );
    }

    final lowerLyrics = song.lyrics.toLowerCase();
    final lowerQuery = searchQuery.toLowerCase();
    final index = lowerLyrics.indexOf(lowerQuery);

    if (index == -1) {
      // Query not found in lyrics, just show the lyrics
      return Text(
        song.lyrics,
        style: TextStyle(fontSize: 13, color: Colors.grey[600]),
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      );
    }

    // Extract the matching portion
    final start = (index - 20).clamp(0, song.lyrics.length);
    final end = (index + searchQuery.length + 20).clamp(0, song.lyrics.length);
    
    final before = song.lyrics.substring(start, index);
    final match = song.lyrics.substring(index, index + searchQuery.length);
    final after = song.lyrics.substring(index + searchQuery.length, end);

    return RichText(
      maxLines: 2,
      overflow: TextOverflow.ellipsis,
      text: TextSpan(
        style: TextStyle(fontSize: 13, color: Colors.grey[600]),
        children: [
          if (start > 0) const TextSpan(text: '...'),
          TextSpan(text: before),
          TextSpan(
            text: match,
            style: const TextStyle(
              color: Color(0xFFFF6347),
              fontWeight: FontWeight.w600,
            ),
          ),
          TextSpan(text: after),
          if (end < song.lyrics.length) const TextSpan(text: '...'),
        ],
      ),
    );
  }
}