# Putting this on GitHub

Two ways. Pick one.

## The no-terminal way, recommended if you are not a coder

1. Download **GitHub Desktop** from https://desktop.github.com and sign in with
   your GitHub account. If you do not have one, make it at github.com, it is free.
2. In GitHub Desktop: **File → Add Local Repository**, choose the `SUBMIT` folder.
3. It will say the folder is not a repository and offer to **create** one. Accept.
4. Type a summary in the box at the bottom left, click **Commit to main**.
5. Click **Publish repository** at the top. Untick *Keep this code private* if you
   want the team to see it without being added.

Done. The URL is at the top of the window.

## The one command way

Open Terminal and paste:

```
bash ~/Desktop/Wapor_2026_hackathon/SUBMIT/PUSH_TO_GITHUB.sh
```

It installs the GitHub tool if needed, signs you in through the browser once,
creates the repository, and pushes. Run it again any time to publish updates.

---

## What gets uploaded

Everything in `SUBMIT`, which is about 30 MB. The raw satellite rasters are left
out on purpose, since they are 45 MB and anyone can regenerate them by running
`05_code/pipeline/gee/01_zonal_to_asset.js` in Earth Engine.

## Giving the team access

If you made the repository **public**, just send the link.

If you made it **private**: on the repository page go to **Settings → Collaborators
→ Add people**, and enter each teammate's GitHub username.
