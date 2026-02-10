# Siri Shortcuts for Homebox

Replace `YOUR_API_URL` below with your deployed Render URL (e.g. `https://homebox-xxxx.onrender.com`).

---

## 1. Setup Homebox (run once per person)

1. Open the **Shortcuts** app → tap **+** to create a new shortcut
2. Name it **Setup Homebox**

### Actions:

1. **Choose from Menu** — prompt: "What would you like to do?"
   - Option 1: **Create New Household**
   - Option 2: **Join Existing Household**

2. **Under "Create New Household":**
   - **Ask for Input** (Text) — prompt: "What's your household name?"  → save as `HouseholdName`
   - **Ask for Input** (Text) — prompt: "What's your name?" → save as `YourName`
   - **Get Contents of URL**:
     - URL: `YOUR_API_URL/households`
     - Method: POST
     - Headers: `Content-Type: application/json`
     - Request Body (JSON):
       ```
       {"household_name": HouseholdName, "your_name": YourName}
       ```
   - Save result as `Response`

3. **Under "Join Existing Household":**
   - **Ask for Input** (Text) — prompt: "Enter the 6-character join code:" → save as `JoinCode`
   - **Ask for Input** (Text) — prompt: "What's your name?" → save as `YourName`
   - **Get Contents of URL**:
     - URL: `YOUR_API_URL/households/join`
     - Method: POST
     - Headers: `Content-Type: application/json`
     - Request Body (JSON):
       ```
       {"join_code": JoinCode, "your_name": YourName}
       ```
   - Save result as `Response`

4. **After the menu (both paths):**
   - **Get Dictionary Value** for key `error` from `Response`
   - **If** result **has any value**:
     - **Show Alert**: `Response.error`
     - **Stop Shortcut**
   - **Otherwise**:
     - **Get Dictionary Value** for key `token` from `Response` → save as `Token`
     - **Save File**: Save `Token` to `Shortcuts/Homebox/token.txt` (iCloud Drive, overwrite)
     - **Get Dictionary Value** for key `join_code` from `Response` → save as `Code`
     - **Show Alert**: "You're all set! Share this code with your household: `Code`"

---

## 2. Add to Homebox (voice-activated)

1. Create a new shortcut named **Add to Homebox**
2. Tap the **(i)** icon → enable **Show in Share Sheet** if desired

### Actions:

1. **Get File**: `Shortcuts/Homebox/token.txt` from iCloud Drive → save as `Token`
2. **Dictate Text** — save as `Dictation`
3. **Get Contents of URL**:
   - URL: `YOUR_API_URL/items`
   - Method: POST
   - Headers:
     - `Content-Type: application/json`
     - `Authorization: Bearer [Token]`
   - Request Body (JSON):
     ```
     {"raw_input": Dictation}
     ```
   - Save result as `Response`
4. **Get Dictionary Value** for key `error` from `Response`
5. **If** result **has any value**:
   - **Speak Text**: `Response.error`
6. **Otherwise**:
   - **Get Dictionary Value** for key `message` from `Response`
   - **Speak Text**: `Response.message`

---

## 3. Find in Homebox (voice-activated)

1. Create a new shortcut named **Find in Homebox**

### Actions:

1. **Get File**: `Shortcuts/Homebox/token.txt` from iCloud Drive → save as `Token`
2. **Dictate Text** — save as `Query`
3. **Get Contents of URL**:
   - URL: `YOUR_API_URL/items/search?q=[Query]`
   - Method: GET
   - Headers:
     - `Authorization: Bearer [Token]`
   - Save result as `Response`
4. **Get Dictionary Value** for key `error` from `Response`
5. **If** result **has any value**:
   - **Speak Text**: `Response.error`
6. **Otherwise**:
   - **Get Dictionary Value** for key `results` from `Response` → save as `Results`
   - **Count** items in `Results`
   - **If** count **is 0**:
     - **Speak Text**: "I didn't find anything matching that."
   - **Otherwise**:
     - **Repeat with each** item in `Results` (limit to first 3):
       - **Get Dictionary Value** for `name` → save as `Name`
       - **Get Dictionary Value** for `location` → save as `Location`
       - **Set Variable** `Speech` to `Speech` + "`Name` is in `Location`. "
     - **Speak Text**: `Speech`

---

## Tips

- Say **"Hey Siri, add to Homebox"** to trigger the add shortcut hands-free
- Say **"Hey Siri, find in Homebox"** to search
- Natural phrasing works: "I put the scissors in the junk drawer" or just "scissors, junk drawer"
- The API handles fuzzy matching, so "bandaid" will find "band-aids"
