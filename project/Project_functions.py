import matplotlib.pyplot as plt
import random
from selenium import webdriver
from bs4 import BeautifulSoup
import time

def no_strategy(data, initial_bet):
    """
    Simulates a random betting strategy in roulette.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        Initial bet amount for the first spin.

    Returns:
    -------
    dict
        Cumulative balances for each bet type ("red", "black", "even", "odd") as lists.

    Notes:
    ------
    - First bet is the initial_bet amount.
    - Subsequent bets are random amounts between $5 and $20.
    - Balances are updated based on wins or losses for each spin.
    """
    # Initialize balances
    balances = {"red": [0], "black": [0], "even": [0], "odd": [0]}

    for spin, (_, row) in enumerate(data.iterrows()):
        
        # Use initial_bet for the first spin; random bet otherwise
        bet = initial_bet if spin == 0 else random.randint(5, 20)
        
        # Update balances
        balances["red"].append(balances["red"][-1] + (bet if row["Red Bet Win"] == 1 else -bet))
        balances["black"].append(balances["black"][-1] + (bet if row["Black Bet Win"] == 1 else -bet))
        balances["even"].append(balances["even"][-1] + (bet if row["Even Bet Win"] == 1 else -bet))
        balances["odd"].append(balances["odd"][-1] + (bet if row["Odd Bet Win"] == 1 else -bet))

    return balances

def martingale_strategy(data, initial_bet):
    """
    Simulates the Martingale betting strategy for roulette.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        Initial bet amount.

    Returns:
    -------
    dict
        Cumulative balances for each bet type ("red", "black", "even", "odd") as lists.

    Notes:
    ------
    - On a win, the bet resets to the initial bet.
    - On a loss, the bet doubles for the next spin.
    """
    # Initialize variables
    balances = {"red": [0], "black": [0], "even": [0], "odd": [0]}
    bets = {"red": initial_bet, "black": initial_bet, "even": initial_bet, "odd": initial_bet}

    for _, row in data.iterrows():
        for bet_type in balances.keys():
            bet = bets[bet_type]

            # Update balances
            if row[f"{bet_type.capitalize()} Bet Win"] == 1:  # Win
                balances[bet_type].append(balances[bet_type][-1] + bet)
                bets[bet_type] = initial_bet  # Reset bet to initial amount
            else:  # Loss
                balances[bet_type].append(balances[bet_type][-1] - bet)
                bets[bet_type] *= 2  # Double the bet amount

    return balances

def fibonacci_strategy(data, initial_bet):
    """
    Simulates the Fibonacci betting strategy for roulette.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        Initial bet amount.

    Returns:
    -------
    dict
        Cumulative balances for each bet type ("red", "black", "even", "odd") as lists.

    Notes:
    ------
    - Bets follow the Fibonacci sequence (e.g., 1, 1, 2, 3, 5, ...) for losses.
    - On a win, the sequence moves back two steps, or resets if at the beginning.
    """
    # Initialize variables
    balances = {"red": [0], "black": [0], "even": [0], "odd": [0]}
    sequences = {"red": [1, 1], "black": [1, 1], "even": [1, 1], "odd": [1, 1]}
    indices = {"red": 0, "black": 0, "even": 0, "odd": 0}

    for _, row in data.iterrows():
        for bet_type in balances.keys():
            current_index = indices[bet_type]
            bet = sequences[bet_type][current_index] * initial_bet

            # Update balances
            if row[f"{bet_type.capitalize()} Bet Win"] == 1:  # Win
                balances[bet_type].append(balances[bet_type][-1] + bet)
                indices[bet_type] = max(0, current_index - 2)
            else:  # Loss
                balances[bet_type].append(balances[bet_type][-1] - bet)
                indices[bet_type] += 1
                if indices[bet_type] >= len(sequences[bet_type]):
                    sequences[bet_type].append(sequences[bet_type][-1] + sequences[bet_type][-2])

    return balances

def d_alembert_strategy(data, initial_bet):
    """
    Simulates the D'Alembert betting strategy for roulette.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        Initial bet amount.

    Returns:
    -------
    dict
        Cumulative balances for each bet type ("red", "black", "even", "odd") as lists.

    Notes:
    ------
    - On a win, the bet decreases by the initial bet.
    - On a loss, the bet increases by the initial bet.
    """
    # Initialize variables
    balances = {"red": [0], "black": [0], "even": [0], "odd": [0]}
    bets = {"red": initial_bet, "black": initial_bet, "even": initial_bet, "odd": initial_bet}

    for _, row in data.iterrows():
        for bet_type in balances.keys():
            bet = bets[bet_type]

            # Update balances
            if row[f"{bet_type.capitalize()} Bet Win"] == 1:  # Win
                balances[bet_type].append(balances[bet_type][-1] + bet)
                bets[bet_type] = max(initial_bet, bet - initial_bet)
            else:  # Loss
                balances[bet_type].append(balances[bet_type][-1] - bet)
                bets[bet_type] += initial_bet

    return balances

def plot_strategies_2x2(data, initial_bet):
    """
    Plots the net profit of four roulette betting strategies in a 2x2 grid.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        The starting bet amount for all strategies.

    Returns:
    -------
    None
        Displays a 2x2 grid of line plots for the net profit of each strategy.

    Notes:
    ------
    - The strategies compared are: No Strategy, Martingale, Fibonacci, and D'Alembert.
    - Each subplot represents one strategy, showing balances for different bet types (Red, Black, Even, Odd).
    - Lines are color-coded for bet types, and a horizontal dashed line represents the starting balance.
    """
    strategies = {
        "No Strategy": no_strategy,
        "Martingale": martingale_strategy,
        "Fibonacci": fibonacci_strategy,
        "D'Alembert": d_alembert_strategy
    }

    colors = ["red", "black", "green", "blue"]  # Define colors for bet types
    titles = [
        "Net Profit Using No Strategy",
        "Net Profit Using the Martingale Strategy",
        "Net Profit Using the Fibonacci Strategy",
        "Net Profit Using the D'Alembert Strategy"
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()  # Flatten the grid for easy iteration

    for i, (strategy_name, strategy_function) in enumerate(strategies.items()):
        balances = strategy_function(data, initial_bet)
        ax = axes[i]

        # Plot balances for each bet type with custom colors
        for j, (bet_type, balance) in enumerate(balances.items()):
            ax.plot(balance, label=bet_type.capitalize(), color=colors[j])

        ax.set_title(titles[i])  # Set the custom title
        ax.set_xlabel("Number of Spins")
        ax.set_ylabel("Net profit ($)")
        ax.axhline(0, color='black', linestyle='--', label="Starting Balance")
        ax.legend()

    plt.tight_layout()
    plt.show()
    
def martingale_strategy_with_table_limits(data, initial_bet, table_limits):
    """
    Simulates the Martingale betting strategy with table limits for multiple bet types.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        The starting bet amount for the Martingale strategy.
    table_limits : list of int
        A list of table limits specifying the maximum allowable bet for each simulation.

    Returns:
    -------
    dict
        A nested dictionary where keys are table limits, and values are dictionaries of bet types
        ("red", "black", "even", "odd") with lists representing the cumulative balance over spins.

    Notes:
    ------
    - Implements the Martingale strategy, doubling the bet after a loss and resetting to the initial bet after a win.
    - Bets are capped by the table limit to prevent exceeding the maximum allowable bet.
    - Tracks balances separately for each combination of table limit and bet type.
    """
    results = {limit: {bet_type: [0] for bet_type in ["red", "black", "even", "odd"]} for limit in table_limits}

    for table_limit in table_limits:
        # Initialize bets
        bets = {bet_type: initial_bet for bet_type in ["red", "black", "even", "odd"]}

        for _, row in data.iterrows():
            for bet_type in bets.keys():
                bet = min(bets[bet_type], table_limit)  # Ensure bet adheres to the table limit

                # Update balances
                if row[f"{bet_type.capitalize()} Bet Win"] == 1:  # Win
                    results[table_limit][bet_type].append(results[table_limit][bet_type][-1] + bet)
                    bets[bet_type] = initial_bet  # Reset bet to initial amount
                else:  # Loss
                    results[table_limit][bet_type].append(results[table_limit][bet_type][-1] - bet)
                    bets[bet_type] = min(bets[bet_type] * 2, table_limit)  # Double the bet, respect table limit

    return results

def fibonacci_strategy_with_table_limits(data, initial_bet, table_limits):
    """
    Simulates the Fibonacci betting strategy with table limits for multiple bet types.

    Parameters:
    ----------
    data : pandas.DataFrame
        DataFrame with roulette outcomes. Columns: "Red Bet Win", "Black Bet Win", "Even Bet Win", "Odd Bet Win".
    initial_bet : int
        The starting bet amount for the Fibonacci strategy.
    table_limits : list of int
        A list of table limits specifying the maximum allowable bet for each simulation.

    Returns:
    -------
    dict
        A nested dictionary where keys are table limits, and values are dictionaries of bet types
        ("red", "black", "even", "odd") with lists representing the cumulative balance over spins.

    Notes:
    ------
    - Implements the Fibonacci betting strategy, where bets follow the Fibonacci sequence.
    - After a win, the bet moves back two steps in the Fibonacci sequence (or resets to the start).
    - After a loss, the bet moves forward one step in the sequence.
    - Bets are capped by the table limit to prevent exceeding the maximum allowable bet.
    - Extends the Fibonacci sequence dynamically as needed for prolonged losses.
    - Tracks balances separately for each combination of table limit and bet type.
    """
    results = {limit: {bet_type: [0] for bet_type in ["red", "black", "even", "odd"]} for limit in table_limits}

    for table_limit in table_limits:
        # Initialize variables
        sequences = {bet_type: [1, 1] for bet_type in ["red", "black", "even", "odd"]}
        indices = {bet_type: 0 for bet_type in ["red", "black", "even", "odd"]}

        for _, row in data.iterrows():
            for bet_type in sequences.keys():
                current_index = indices[bet_type]
                bet = min(sequences[bet_type][current_index] * initial_bet, table_limit)  # Adhere to table limit

                # Update balances
                if row[f"{bet_type.capitalize()} Bet Win"] == 1:  # Win
                    results[table_limit][bet_type].append(results[table_limit][bet_type][-1] + bet)
                    indices[bet_type] = max(0, current_index - 2)  # Move back two steps in the sequence
                else:  # Loss
                    results[table_limit][bet_type].append(results[table_limit][bet_type][-1] - bet)
                    indices[bet_type] += 1
                    # Extend Fibonacci sequence if needed
                    if indices[bet_type] >= len(sequences[bet_type]):
                        sequences[bet_type].append(sequences[bet_type][-1] + sequences[bet_type][-2])

    return results

def plot_strategies_2x4(martingale_data, fibonacci_data, table_limits):
    """
    Plots the results of Martingale and Fibonacci strategies across multiple bet types 
    and table limits in a 2x4 grid layout.

    Parameters:
    ----------
    martingale_data : dict
        Nested dictionary containing Martingale strategy results. 
        Keys are table limits, and values are dictionaries of bet types ("red", "black", "even", "odd") 
        with lists representing the cumulative balances over spins.
    fibonacci_data : dict
        Nested dictionary containing Fibonacci strategy results. 
        Same structure as `martingale_data`.
    table_limits : list of int
        List of table limits used to distinguish plotted lines.

    Notes:
    ------
    - The top row of plots corresponds to Martingale strategy results, and the bottom row corresponds to Fibonacci.
    - Each column represents one of the bet types: "red", "black", "even", or "odd".
    - Lines for each table limit are plotted within each subplot, and balances are compared.
    - A horizontal dashed line marks the starting balance (0).
    - Subplots share the y-axis for rows to allow easier comparison of balance changes.

    Returns:
    -------
    None
        Displays the plot directly.
    """
    bet_types = ["red", "black", "even", "odd"]
    strategies = [("Martingale", martingale_data), ("Fibonacci", fibonacci_data)]
    
    fig, axes = plt.subplots(2, 4, figsize=(20, 10), sharey='row')

    for row, (strategy_name, strategy_data) in enumerate(strategies):
        for col, bet_type in enumerate(bet_types):
            ax = axes[row, col]
            for table_limit in table_limits:
                balances = strategy_data[table_limit][bet_type]
                ax.plot(balances, label=f"Table Limit: ${table_limit}")
            ax.set_title(f"{strategy_name} Strategy: Betting on {bet_type.capitalize()}")
            ax.set_xlabel("Number of Spins")
            ax.axhline(0, color='black', linestyle='--', label="Starting Balance")
            if col == 0:  # Add ylabel only to the first column in each row
                ax.set_ylabel("Net profit ($)")
            ax.legend()

    plt.tight_layout()
    plt.show()

def extract_roulette_max_bets():
    """
    Extracts maximum roulette bet limits for tables from a specific webpage.

    This function uses Selenium to navigate to a webpage containing table bet limits for online roulette games.
    It extracts the maximum bet values for tables by parsing the webpage's HTML using BeautifulSoup.

    Returns:
        list: A list of strings representing the maximum bet limits for roulette tables.

    Notes:
        - This function requires the Selenium WebDriver for Chrome to be installed and properly set up.
        - The webpage structure or class names may change, which could break the functionality of this function.
    """
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    url = 'https://www.livedealer.org/live-casino-games/table-bet-limits/'
    driver.get(url)

    # Wait for the page to load completely
    time.sleep(5)

    # Get the fully rendered HTML
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table', {'class': 'sortable responsive-table'})

    # Extract data from the table
    large_table_data = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        columns = row.find_all('td')
        roulette_max_bet = columns[4].get_text(strip=True)
        large_table_data.append(roulette_max_bet)

    # Close the browser
    driver.quit()

    return large_table_data

def extract_roulette_max_bets_last_row():
    """
    Extracts maximum roulette bet limits from the last row of tables from a specific webpage.

    This function uses Selenium to navigate to a webpage containing table bet limits for online roulette games.
    It extracts the maximum bet values from the last row of tables by parsing the webpage's HTML using BeautifulSoup.

    Returns:
        list: A list of strings representing the maximum bet limits for roulette tables.

    Notes:
        - This function requires the Selenium WebDriver for Chrome to be installed and properly set up.
        - The webpage structure or class names may change, which could break the functionality of this function.
    """
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    url = 'https://roulette77.us/blog/explanation-of-betting-limits'
    driver.get(url)

    # Wait for the page to load completely
    time.sleep(5)

    # Get the fully rendered HTML
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table', {'class': 'classic-table classic-table--min600'})

    # Find all the rows in the table and get the last row
    rows = table.find_all('tr')
    last_row = rows[-1]

    # Extract the columns from the last row
    columns = last_row.find_all('td')
    small_table_data = [
        columns[2].text.strip(),  
        columns[4].text.strip(),  
        columns[6].text.strip()   
    ]

    # Close the browser
    driver.quit()

    return small_table_data