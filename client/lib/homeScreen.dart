import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: <Widget>[
            Image.asset(
              'assets/logo.png',
              height: 80,
              width: 100,
            ),
            const SizedBox(width: 10),
            const Text("Ratatui"),
          ],
        ),
      ),
      body: RecipeCard(),
    );
  }
}

class RecipeCard extends StatefulWidget {
  @override
  _RecipeCardState createState() => _RecipeCardState();
}

class _RecipeCardState extends State<RecipeCard> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  TextEditingController ingredientsController = TextEditingController();

  Future<void> generateRecipeByAI(String ingredients) async {
    final apiUrl = 'http://localhost:8000/api/generate-recipes/';
    final response = await http.post(
      Uri.parse(apiUrl),
      body: json.encode({"items": [ingredients]}),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final responseData = json.decode(response.body);
      final generatedRecipe = responseData['output_text'][0];

      // Store the generated recipe in Firestore
      final CollectionReference recipes =
          FirebaseFirestore.instance.collection('recipes');
      String recipeId = DateTime.now().millisecondsSinceEpoch.toString();
      await recipes.add({
        'id': recipeId,
        'name': 'Generated Recipe',
        'ingredients': ingredients,
        'steps': generatedRecipe,
      });

      // Clear the text field after generating and storing the recipe
      setState(() {
        ingredientsController.clear();
      });
      
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Recipe generated and stored successfully!'),
      ));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Failed to generate recipe. Please try again.'),
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextFormField(
                  controller: ingredientsController,
                  decoration: const InputDecoration(
                    labelText: 'Ingredients',
                  ),
                  validator: (value) {
                    if (value!.isEmpty) {
                      return 'Please enter your recipe Ingredients';
                    }
                    return null;
                  },
                  maxLines: 5,
                ),
                SizedBox(height: 16.0),
                ElevatedButton(
                  onPressed: () {
                    if (_formKey.currentState?.validate() ?? false) {
                      generateRecipeByAI(ingredientsController.text);
                    }
                  },
                  child: Text("Generate Recipe by AI"),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
