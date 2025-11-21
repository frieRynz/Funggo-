import 'package:flutter/material.dart';
import 'package:funggu/services/api_service.dart';
import '../models/song.dart';
import '../services/mock_database.dart';
import '../widgets/song_card.dart';
import '../services/api_service.dart';
import 'package:http/http.dart' as http;


class LandingPage extends StatefulWidget {
  const LandingPage({Key? key}) : super(key: key);

  @override
  State<LandingPage> createState() => _FirstPageState();
}

class _FirstPageState extends State<LandingPage> {
  final TextEditingController _searchController = TextEditingController();
  List<Song> _searchResults = [];
  bool _isLoading = false;
  bool _hasSearched = false;

  Future<void> _performSearch() async{
    if (_searchController.text.isEmpty) return;

    FocusScope.of(context).unfocus();

    setState(() {
      _isLoading = true;
      _hasSearched = true;
    });

    // Simulate network delay
    // Future.delayed(const Duration(milliseconds: 800), () {
    //   if (mounted) {
    //     setState(() {
    //       _searchResults = MockDatabase.searchSongs(_searchController.text);
    //       // _searchResults = await ApiService.searchSongs(_searchController.text);
    //       _isLoading = false;
    //     });
    //   }
    // });
    try{
      final songs = await ApiService.searchSongs(_searchController.text);
      if(mounted){
        setState(() {
          _searchResults = songs;
          _isLoading = false;
        });
      }
    }catch (e){
      if(mounted){
        setState(() {
          _searchResults = [];
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Top section with logo and search
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  if (!_hasSearched) ...[
                    const SizedBox(height: 120),
                    // Logo
                    Image.asset(
                      'images/logo_landing.png',
                      width: 190,
                      height: 190,
                    ),
                  ] else ...[
                    const SizedBox(height: 20),
                    // Horizontal logo appears after first search
                    Image.asset(
                      'images/logo_horizon.png',
                      height: 50,
                    ),
                    const SizedBox(height: 16),
                  ],
                  // Search input
                  TextField(
                    controller: _searchController,
                    onSubmitted: (_) => _performSearch(),
                    decoration: InputDecoration(
                      hintText: "What's that song??",
                      hintStyle: TextStyle(color: Colors.grey[600]),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 14,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Search button
                  SizedBox(
                    
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _performSearch,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2C2C2C),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text(
                        'Search',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.deepOrange,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Results section
            Expanded(
              child: _isLoading
                  ? Center(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: List.generate(
                          3,
                          (index) => Container(
                            margin: const EdgeInsets.symmetric(horizontal: 4),
                            width: 16,
                            height: 16,
                            decoration: const BoxDecoration(
                              color: Color(0xFFFF6347),
                              shape: BoxShape.circle,
                            ),
                          ),
                        ),
                      ),
                    )
                  : _hasSearched
                  ? _searchResults.isEmpty
                        ? const Center(
                            child: Text(
                              'No results found',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
                              ),
                            ),
                          )
                        : ListView(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24.0,
                            ),
                            children: [
                              const Text(
                                'Your results :',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 16),
                              ..._searchResults.map(
                                (song) => SongCard(
                                  song: song,
                                  searchQuery: _searchController.text,
                                ),
                              ),
                            ],
                          )
                  : const SizedBox.shrink(),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}
