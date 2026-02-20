import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from photos.models import UserPostInteraction, Post

def collaborative_recommend(user_id, top_n=5):
    interactions = UserPostInteraction.objects.all().values('user_id', 'post_id', 'weight')
    df = pd.DataFrame(interactions)
    
    if df.empty:
        return []

    # Aggregate duplicate user-post interactions
    df = df.groupby(['user_id', 'post_id'], as_index=False)['weight'].sum()

    # Now pivot
    user_post_matrix = df.pivot(index='user_id', columns='post_id', values='weight').fillna(0)
    
    similarity_matrix = cosine_similarity(user_post_matrix.T)
    sim_df = pd.DataFrame(similarity_matrix, index=user_post_matrix.columns, columns=user_post_matrix.columns)

    if user_id not in user_post_matrix.index:
        return []  # User has no interactions yet

    user_interactions = user_post_matrix.loc[user_id]
    interacted_posts = user_interactions[user_interactions > 0].index.tolist()

    scores = {}
    for post in interacted_posts:
        similar_posts = sim_df[post].sort_values(ascending=False)
        for p, score in similar_posts.items():
            if p not in interacted_posts:
                scores[p] = scores.get(p, 0) + score * user_interactions[post]

    recommended_posts = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [post_id for post_id, _ in recommended_posts]

# --------------------------
# Content-Based Filtering
# --------------------------
def content_recommend(post_id, top_n=5):
    posts = Post.objects.all().values('id', 'style', 'caption')
    post_df = pd.DataFrame(posts)
    
    # Encode style
    post_df = pd.get_dummies(post_df, columns=['style'])
    
    # Text features: caption + style
    post_df['text_features'] = post_df['caption'].fillna('') + ' ' + post_df[[
        col for col in post_df.columns if col.startswith('style_')
    ]].apply(lambda x: ' '.join(x.index[x==1]), axis=1)
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(post_df['text_features'])
    
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    idx = post_df[post_df['id']==post_id].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [i for i in sim_scores if i[0] != idx]  # exclude self
    top_indices = [i[0] for i in sim_scores[:top_n]]
    return post_df.iloc[top_indices]['id'].tolist()