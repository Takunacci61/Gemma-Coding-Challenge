import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'bottom_menu.dart';

class GoalsPage extends StatefulWidget {
  @override
  _GoalsPageState createState() => _GoalsPageState();
}

class _GoalsPageState extends State<GoalsPage> {
  List<dynamic> goals = [];
  bool isLoading = true;
  bool isSubmitting = false;
  String? accessToken;
  String? errorMessage;

  Future<void> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      accessToken = prefs.getString('access');
    });
  }

  Future<void> fetchGoals() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    await getToken();

    try {
      final url = Uri.parse('/planner/goals/');
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          goals = json.decode(response.body);
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Failed to fetch goals: ${response.statusCode}';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'An error occurred while fetching goals';
        isLoading = false;
      });
      print('Error: $e');
    }
  }

  Future<void> createGoal(Map<String, dynamic> goalData) async {
    setState(() {
      isSubmitting = true;
      errorMessage = null;
    });

    try {
      final url = Uri.parse('/planner/goals/');
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode(goalData),
      );

      if (response.statusCode == 201) {
        await fetchGoals();
        setState(() {
          isSubmitting = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Goal created successfully')),
        );
      } else {
        setState(() {
          errorMessage = 'Failed to create goal: ${response.statusCode}';
          isSubmitting = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'An error occurred while creating goal';
        isSubmitting = false;
      });
      print('Error: $e');
    }
  }

  void showGoalDetailsModal(BuildContext context, Map<String, dynamic> goal) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Text(
            goal['goal_name'],
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Description: ${goal['goal_description']}'),
                SizedBox(height: 8),
                Text('Start Date: ${goal['goal_start_date']}'),
                Text('End Date: ${goal['goal_end_date']}'),
                SizedBox(height: 8),
                Text('Status: ${goal['status']}'),
                Text('Feasibility Score: ${goal['feasibility_score']}'),
                SizedBox(height: 8),
                Text('Notes: ${goal['model_notes']}'),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Close'),
            ),
          ],
        );
      },
    );
  }

  void showCreateGoalModal(BuildContext context) {
    final TextEditingController goalNameController = TextEditingController();
    final TextEditingController goalDescriptionController = TextEditingController();
    DateTime startDate = DateTime.now();
    DateTime endDate = DateTime.now().add(Duration(days: 7));

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setStateModal) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Text('Create Goal'),
              content: SingleChildScrollView(
                child: Column(
                  children: [
                    TextField(
                      controller: goalNameController,
                      decoration: InputDecoration(
                        labelText: 'Goal Name',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    SizedBox(height: 10),
                    TextField(
                      controller: goalDescriptionController,
                      decoration: InputDecoration(
                        labelText: 'Goal Description',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      maxLines: 3,
                    ),
                    SizedBox(height: 10),
                    ListTile(
                      title: Text('Start Date: ${startDate.toLocal().toString().split(' ')[0]}'),
                      trailing: Icon(Icons.calendar_today),
                      onTap: () async {
                        DateTime? picked = await showDatePicker(
                          context: context,
                          initialDate: startDate,
                          firstDate: DateTime(2000),
                          lastDate: DateTime(2101),
                        );
                        if (picked != null) {
                          setStateModal(() {
                            startDate = picked;
                          });
                        }
                      },
                    ),
                    ListTile(
                      title: Text('End Date: ${endDate.toLocal().toString().split(' ')[0]}'),
                      trailing: Icon(Icons.calendar_today),
                      onTap: () async {
                        DateTime? picked = await showDatePicker(
                          context: context,
                          initialDate: endDate,
                          firstDate: startDate,
                          lastDate: DateTime(2101),
                        );
                        if (picked != null) {
                          setStateModal(() {
                            endDate = picked;
                          });
                        }
                      },
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: isSubmitting
                      ? null
                      : () async {
                    if (goalNameController.text.isEmpty ||
                        goalDescriptionController.text.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Please fill all fields')),
                      );
                      return;
                    }

                    Navigator.pop(context);
                    await createGoal({
                      "goal_name": goalNameController.text,
                      "goal_description": goalDescriptionController.text,
                      "goal_start_date": startDate.toLocal().toString().split(' ')[0],
                      "goal_end_date": endDate.toLocal().toString().split(' ')[0],
                    });
                  },
                  child: isSubmitting
                      ? CircularProgressIndicator(strokeWidth: 2)
                      : Text('Create'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  void initState() {
    super.initState();
    fetchGoals();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Goals'),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue, Colors.lightBlueAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : errorMessage != null
          ? Center(
        child: Text(
          errorMessage!,
          style: TextStyle(fontSize: 16, color: Colors.red),
        ),
      )
          : goals.isEmpty
          ? Center(
        child: Text(
          'No goals available',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      )
          : ListView.builder(
        itemCount: goals.length,
        itemBuilder: (context, index) {
          final goal = goals[index];
          return Card(
            elevation: 4,
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: ListTile(
              title: Text(
                goal['goal_name'],
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text('Status: ${goal['status']}'),
              trailing: Icon(Icons.arrow_forward, color: Colors.blue),
              onTap: () => showGoalDetailsModal(context, goal),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => showCreateGoalModal(context),
        child: Icon(Icons.add),
        backgroundColor: Colors.blue,
      ),
      bottomNavigationBar: BottomMenu(),
    );
  }
}
