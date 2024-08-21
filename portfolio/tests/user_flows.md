* User visit site: is presented with a login screen if not logged in.
Test Cases: 
- Not logged in user always redirects to login page
- Logout takes to login page, which always has the overview page as next page if not requested explicitly

* User logs in and sees the overview page
Test Cases:
- Global portfolio summary must be visible. If nothing is added, this shows 0. Else, correct
  summary must be displayed.
- Summary includes: 
    * Net worth
    * Number of accounts with a call-to-action to detail page
    * Monthly plot of networth
    * Alerts

* User goes to Accounts page from Menu and finds no accounts. Clicks on a button to add new account, and sees a form. Fills the form and an account is created. The page now shows the account summary card and the add account option.
* The user adds other accounts, such as broker, demat, crypto etc.
* In each account, the user sees the transactions tab. Can visit the transactions tab to see a short pass-book (initially empty). Plus, a button to add new transaction is available. The user clicks on it and a menu pops up with fields rendered according to the account type. An option to upload bulk transactions for the account is also available. The user uploads a transaction file and the account details are updated.
* The overview page starts showing summary information.