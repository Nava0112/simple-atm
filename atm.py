from flask import Flask, render_template, request, redirect, url_for, session
import traceback
import apminsight  # Make sure this is configured per Site24x7 docs

app = Flask(__name__)
app.secret_key = 'secret123'

# Sample 5 user accounts
users = {
    1001: {'accno': 1001, 'username': 'Nava', 'pass': 1111, 'amount': 10000},
    1002: {'accno': 1002, 'username': 'Ava', 'pass': 2222, 'amount': 15000},
    1003: {'accno': 1003, 'username': 'Sam', 'pass': 3333, 'amount': 20000},
    1004: {'accno': 1004, 'username': 'Lia', 'pass': 4444, 'amount': 5000},
    1005: {'accno': 1005, 'username': 'Jay', 'pass': 5555, 'amount': 2500}
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            accno = int(request.form['accno'])
            pin = int(request.form['pin'])
            app.logger.info(f"Login attempt for account {accno}")

            user = users.get(accno)
            if not user:
                app.logger.warning(f"Login failed: Account {accno} not found")
                return render_template('login.html', error="Account number does not exist.")
            elif user['pass'] != pin:
                app.logger.warning(f"Login failed: Incorrect PIN for account {accno}")
                return render_template('login.html', error="Incorrect PIN.")
            else:
                session['logged_in'] = True
                session['accno'] = accno
                app.logger.info(f"Login successful for account {accno}")
                return redirect('/menu')
        except Exception as e:
            app.logger.error(f"Exception during login: {str(e)}")
            traceback.print_exc()
            # Here, we return a friendly error, but you could also raise to make it uncaught
            return render_template('login.html', error="An error occurred during login. Please try again.")
    return render_template('login.html')

@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect('/')
    accno = session['accno']
    user = users[accno]
    return render_template('menu.html', username=user['username'], accno=accno)

@app.route('/balance')
def balance():
    if not session.get('logged_in'):
        return redirect('/')
    try:
        accno = session['accno']
        balance = users[accno]['amount']
        app.logger.info(f"Balance viewed for account {accno}")
        return render_template('balance.html', balance=balance)
    except Exception as e:
        app.logger.error(f"Error viewing balance: {e}")
        raise  # Re-raise to let APM catch the exception

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if not session.get('logged_in'):
        return redirect('/')
    accno = session['accno']
    if request.method == 'POST':
        try:
            amt = int(request.form['amount'])
            if amt <= 0:
                raise ValueError("Amount must be positive")
            users[accno]['amount'] += amt
            app.logger.info(f"Deposit: ₹{amt} to account {accno}")
            return redirect('/balance')
        except Exception as e:
            app.logger.error(f"Deposit failed: {e}")
            raise  # Re-raise to let APM catch the exception
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if not session.get('logged_in'):
        return redirect('/')
    accno = session['accno']
    if request.method == 'POST':
        try:
            amt = int(request.form['amount'])
            if amt <= 0:
                raise ValueError("Amount must be positive")
            if amt <= users[accno]['amount']:
                users[accno]['amount'] -= amt
                app.logger.info(f"Withdraw: ₹{amt} from account {accno}")
                return redirect('/balance')
            else:
                app.logger.warning(f"Withdraw failed: insufficient funds in account {accno}")
                return render_template('withdraw.html', error="Insufficient balance.")
        except Exception as e:
            app.logger.error(f"Withdraw failed: {e}")
            raise  # Re-raise to let APM catch the exception
    return render_template('withdraw.html')

@app.route('/logout')
def logout():
    accno = session.get('accno', 'Unknown')
    session.clear()
    app.logger.info(f"User logged out from account {accno}")
    return redirect('/')

# Test route to trigger an uncaught exception for APM
@app.route('/trigger-exception')
def trigger_exception():
    raise ValueError("This is an uncaught exception for Site24x7 APM")

if __name__ == '__main__':
    app.run(debug=True)
