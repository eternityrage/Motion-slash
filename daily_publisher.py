import os
import json
import glob
import random
import requests
import shutil
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Import upload functions
try:
    from upload.upload_instagram import upload_to_instagram
    from upload.upload_threads import upload_to_threads
    from upload.upload_facebook import upload_to_facebook, upload_to_facebook_story
    from upload.upload_to_youtube import upload_to_youtube
except ImportError as e:
    print(f"Error importing upload modules: {e}")
    # Still want to proceed or stop?
    pass

PROCESSED_DIR = "Processed_Videos"
PUBLISHED_LOG = "published_videos.json"

def get_already_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def get_repost_counts():
    """Count how many times each video has been posted."""
    published = get_already_published()
    counts = {}
    for entry in published:
        vname = entry.get("video_name", "")
        counts[vname] = counts.get(vname, 0) + 1
    return counts

def mark_as_published(video_name, metadata):
    published = get_already_published()
    published.append({
        "video_name": video_name,
        "metadata": metadata
    })
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(published, f, indent=4)

def select_video(specific_video=None):
    published = [item["video_name"] for item in get_already_published()]
    all_videos = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.mp4")))

    if specific_video:
        # specific_video might be a full path or just a filename
        if os.path.exists(specific_video):
            # It's a full path
            vid_path = specific_video
            name = os.path.basename(specific_video)
        else:
            # It's just a filename, join with PROCESSED_DIR
            vid_path = os.path.join(PROCESSED_DIR, specific_video)
            name = specific_video

        if os.path.exists(vid_path):
            if name in published:
                post_count = sum(1 for p in published if p == name)
                print(f"🔄 Video {name} was already published ({post_count}x) - Re-publishing (recycling)")
            return vid_path, name
        else:
            print(f"❌ Error: Specific video {name} not found")
            return None, None

    # Find unpublished videos first
    unpublished = [(vid, os.path.basename(vid)) for vid in all_videos if os.path.basename(vid) not in published]

    if unpublished:
        vid, name = unpublished[0]
        return vid, name

    # All videos published - use weighted random selection (less posted = more likely)
    if all_videos:
        repost_counts = get_repost_counts()
        weights = []
        for vid in all_videos:
            name = os.path.basename(vid)
            count = repost_counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        selected_vid = random.choices(all_videos, weights=weights, k=1)[0]
        name = os.path.basename(selected_vid)
        post_count = repost_counts.get(name, 0)
        print(f"🎲 All videos published. Weighted random reuse (posted {post_count}x): {name}")
        return selected_vid, name

    return None, None

def generate_caption():
    import random
    import time

    api_key = os.getenv("POLLINATIONS_API_KEY")
    model = os.getenv("AI_MODEL", "openai")

    fallback_titles = [
        "This duel ended in 0.3 seconds ⚔️",
        "Speed. Power. No Mercy. 🔥",
        "Who wins this stickman battle? ⚔️",
        "Anime-style fight choreography 🥷",
        "Ultra-fast stickman sword fight 💨",
        "When stickmen take things too far ⚔️",
        "Minimalist action at its finest 🎬",
        "The fastest blade in the west ⚡",
        "Stickman duel — no rules, no mercy 🔥",
        "POV: You're a stickman in a death match ⚔️",
        "Parallel slash technique 🥷",
        "One hit. One kill. 💀",
        "Stickman sword fight choreography 🩸",
        "This animation is CRIMINALLY underrated 🔥",
        "They don't teach this in stickman school ⚔️",
    ]

    fallback_descriptions = [
        "⚔️ Ultra-fast stickman battles — Speed. Power. No Mercy. These stickmen don't play by any rules. Watch the fastest blade in action and drop a 🔥 if you want more anime-style stickman fights! Every duel is choreographed for maximum impact. Short, punchy, high-intensity action reels daily. Like and follow for daily stickman sword fights! #stickmanfight #animation #swordfight #anime #action #stickman #fightchoreography #minimalist #battle #speed #power #nomercy #duel #martialarts #stickmananimation",
        "🎬 Daily minimalist action reels. Stickman sword fights with anime-inspired choreography. Every move is calculated, every strike is lethal. These stickmen live for the battle. Comment who you think wins this duel! Like if you want to see more stickman battles. Follow for daily action content that hits different. #stickmanfight #animation #anime #swordfight #action #stickman #battle #choreography #minimalist #speed #duel #fighter #martialarts #stickmananimation #animefight",
        "🩸 Anime-inspired fight choreography meets minimalist stickman aesthetics. Pure speed, pure power, no mercy. These stickmen train their whole lives for a 3-second duel. Drop a 🔥 if this animation impressed you! Like and share to support the channel. More stickman fights dropping every day. Which move was your favorite? #stickmanfight #swordfight #animation #anime #action #stickman #fightchoreography #battle #minimalist #speed #power #samurai #warrior #duel #stickmananimation",
        "Speed. Power. No Mercy. That's the stickman code. ⚔️ Every animation is crafted for maximum hype — short, brutal, and absolutely stunning. These stickmen move faster than the eye can see. Like and follow for your daily dose of action-packed stickman battles. Comment your favorite fight scene! 🔥 #stickmanfight #animation #action #anime #swordfight #stickman #battle #choreography #speed #minimalist #duel #fighter #epicfights #stickmananimation #combat",
        "Not all heroes wear capes. Some are just stickmen with swords. ⚔️ These minimalist action reels pack more heat than most big-budget animations. Pure fight choreography, zero filler. If you love sword fights, anime-style action, or just watching stickmen go absolutely crazy — you're in the right place. Drop a like and subscribe to the stickman battlefield! #stickmanfight #animation #anime #action #swordfight #stickman #battle #choreography #minimalist #speed #duel #fighter #stickmananimation #epic #animefight",
        "⚔️ Stickman Sword Fights — where every frame is a masterpiece of minimalist action. These stickmen move with precision, speed, and lethal intent. No dialogue. No drama. Just pure, unfiltered combat. If you're into fight choreography and anime-style action, you'll love what we post daily. Like and follow to never miss a battle! Drop a comment and tell us who won! 🔥 #stickmanfight #swordfight #animation #anime #action #stickman #battle #choreography #duel #speed #power #fighter #stickmananimation #combat #epic",
        "The stickman code: fight fast, fight hard, show no mercy. 🥷 Every day we bring you the most intense stickman sword fights on the internet. Anime-inspired choreography mixed with minimalist aesthetics. Short clips that hit different. Follow for daily action and drop a 🔥 if you're part of the stickman squad! #stickmanfight #animation #anime #action #swordfight #stickman #battle #choreography #minimalist #duel #speed #fighter #stickmananimation #epic #animefight",
        "They say size doesn't matter. Tell that to the stickman with a sword. ⚔️ These little warriors pack more heat than entire armies. Every duel is a masterclass in speed and precision. Minimalist animation, maximum impact. Like and follow for your daily stickman fix. Comment '⚔️' if you want more sword fights! #stickmanfight #animation #swordfight #anime #action #stickman #battle #choreography #minimalist #speed #power #duel #fighter #stickmananimation #combat",
        "You blinked. You missed it. That's stickman sword fighting at its finest. ⚡ Speed. Power. No Mercy. These warriors don't waste a single frame. Every move is deliberate, every strike is devastating. Follow for daily minimalist action reels that hit harder than your morning coffee. Drop a 🔥 for the stickman gang! #stickmanfight #animation #action #anime #swordfight #stickman #battle #choreography #speed #minimalist #duel #fighter #stickmananimation #epic #animefight",
        "When the beat drops, the blades come out. 🎵⚔️ Stickman Sword Fights brings you daily action reels with anime-inspired choreography and zero wasted motion. These stickmen move to their own rhythm — the rhythm of battle. Like and follow if you appreciate the art of the blade. Comment who you think has the best technique! #stickmanfight #swordfight #animation #anime #action #stickman #battle #choreography #minimalist #speed #power #duel #fighter #stickmananimation #combat",
        "This stickman didn't skip leg day. Or sword day. ⚔️ Every day we post the most intense stickman battles you've ever seen. Minimalist animation. Maximum adrenaline. If you love fight choreography and anime-style action, you're home. Drop a like and join the stickman army! 🪖 #stickmanfight #animation #action #anime #swordfight #stickman #battle #choreography #speed #minimalist #duel #fighter #stickmananimation #epic #animefight",
        "Stickman Sword Fights: where speed meets power and mercy is optional. 💀 Our stickmen train in the ancient art of ultra-fast combat. Every video is a window into their world of perpetual battle. Like and follow for your daily dose of minimalist action. Comment your favorite fighting style! 🔥 #stickmanfight #swordfight #animation #anime #action #stickman #battle #choreography #minimalist #duel #speed #power #fighter #stickmananimation #combat",
    ]

    if not api_key:
        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        print("Warning: POLLINATIONS_API_KEY not found. Using fallback captions.")
        return chosen_title, chosen_desc

    vibes = [
        "hyped and explosive — describe the fight as ultra-fast, intense, and unstoppable",
        "competitive and challenging — hype up the duel and ask viewers who they think would win",
        "cinematic and epic — describe the fight like an anime battle scene with dramatic flair",
        "minimalist and punchy — short, sharp, high-impact action description",
        "playful and engaging — add some humor about stickmen being surprisingly deadly",
        "intense and dramatic — focus on the speed, precision, and lethal moves of the fighters",
        "mysterious and cool — describe the stickmen as silent warriors from a hidden dojo",
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a completely unique, short punchy title and a captivating description for a stickman sword fight "
        f"animation video for the Instagram page 'Stickman Sword Fights'. "
        f"The page posts daily minimalist action reels — ultra-fast stickman battles with anime-inspired fight choreography. "
        f"Speak as the page admin — hyped, energetic, and passionate about stickman battles. "
        f"Make the vibe {chosen_vibe}. "
        f"The description should be MEDIUM (2-4 sentences), action-packed, and engaging. "
        f"Include engagement calls-to-action such as: "
        f"- Drop a 🔥 if you want more stickman battles! "
        f"- Comment who wins this duel! "
        f"- Like and follow for daily stickman fights! "
        f"- Share with a fellow animation fan! "
        f"Include relevant hashtags in ALL LOWERCASE such as #stickmanfight #animation #swordfight #anime #action #stickman #fightchoreography #minimalist #battle #speed #power #nomercy #duel. "
        f"Return ONLY a valid JSON object in this format: {{\"title\": \"<title>\", \"description\": \"<description>\"}} "
        f"Do not include any other text or markdown block backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "seed": random.randint(1, 999999)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        return result.get("title", chosen_title), result.get("description", chosen_desc)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

def main():
    print("=" * 60)
    print("🚀 DAILY AUTOMATION STARTING")
    print("=" * 60)
    
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None
    video_path, video_name = select_video(specific_video)
    if not video_path:
        print("✅ No new videos found to publish. Exiting.")
        return
        
    print(f"👉 Selected Video: {video_name}")
    print("🧠 Generating caption via Pollination AI...")
    title, description = generate_caption()
    
    print(f"📝 Title: {title}")
    print(f"📝 Description:\n{description}")
    
    # Combined caption for platforms that use a single text field
    combined_caption = f"{title}\n\n{description}"
    
    success_flags = {
        "instagram_reel": False,
        "instagram_story": False,
        "facebook_reel": False,
        "facebook_story": False,
        "threads": False,
        "youtube": False
    }
    
    # Instagram Reels
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=False)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_reel"] = True
    except Exception as e:
        print(f"❌ Instagram Reel upload failed: {e}")
        
    # Instagram Stories
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=True)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_story"] = True
    except Exception as e:
        print(f"❌ Instagram Story upload failed: {e}")
        
    # Facebook Reels
    try:
        result = upload_to_facebook(video_path, description, title=title)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_reel"] = True
    except Exception as e:
        print(f"❌ Facebook Reel upload failed: {e}")
        
    # Facebook Stories
    try:
        result = upload_to_facebook_story(video_path)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_story"] = True
    except Exception as e:
        print(f"❌ Facebook Story upload failed: {e}")
        
    # Threads
    try:
        result = upload_to_threads(video_path, combined_caption)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Threads: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["threads"] = True
    except Exception as e:
        print(f"❌ Threads upload failed: {e}")
        
    # YouTube Shorts
    try:
        upload_to_youtube(video_path, title, description, tags=["stickman fight", "animation", "sword fight", "anime", "action", "stickman", "fight choreography", "minimalist", "battle", "speed", "power", "no mercy", "duel", "stickman animation", "anime fight"])
        success_flags["youtube"] = True
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        
    # Record as published regardless of partial success,
    # to avoid repeating the same video. Alternatively, only record if fully successful.
    print("\n✅ Marking video as published.")
    
    # Check if this is a recycled video (already in published_videos.json)
    published_list = get_already_published()
    is_recycled = any(item["video_name"] == video_name for item in published_list)
    
    if is_recycled:
        print(f"   🔄 This is a recycled video (re-publishing)")
    
    mark_as_published(video_name, {
        "title": title,
        "description": description,
        "success_flags": success_flags,
        "recycled": is_recycled
    })
    
    # Move the published video to Published_Videos folder
    published_dir = "Published_Videos"
    if not os.path.exists(published_dir):
        os.makedirs(published_dir)
        
    try:
        dest_path = os.path.join(published_dir, video_name)
        shutil.move(video_path, dest_path)
        print(f"📦 Moved published video to {dest_path}")
    except Exception as e:
        print(f"❌ Failed to move published video: {e}")
    
    print("🎉 DAILY AUTOMATION COMPLETE")

if __name__ == "__main__":
    main()
