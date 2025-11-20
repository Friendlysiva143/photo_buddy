from django.shortcuts import render, redirect
def demo_chat_list(request):
    # Fake user buddies
    chat_users = [
        {'id': 1, 'username': 'alice'},
        {'id': 2, 'username': 'bob'},
        {'id': 3, 'username': 'carol'},
    ]
    return render(request, 'chat/demo_chat_list.html', {'chat_users': chat_users})
def demo_chat_conversation(request, buddy_id):
    # Map of user IDs to names
    user_map = {1: 'alice', 2: 'bob', 3: 'carol'}
    buddy_username = user_map.get(buddy_id, 'Unknown User')
    
    # Fake messages for demo
    sample_conversation = [
        {'sender': 'alice', 'message': 'Hi Bob!', 'timestamp': '13:23'},
        {'sender': 'bob', 'message': 'Hello Alice, how are you?', 'timestamp': '13:24'},
        {'sender': 'alice', 'message': "I'm good, thanks for asking!", 'timestamp': '13:25'},
    ] if buddy_id == 2 else [
        {'sender': 'alice', 'message': f"Hi {buddy_username}!", 'timestamp': '13:23'},
        {'sender': buddy_username, 'message': f"Hello Alice!", 'timestamp': '13:24'},
    ]
    return render(request, 'chat/demo_chat.html', {
        'buddy_username': buddy_username,
        'messages': sample_conversation,
    })
