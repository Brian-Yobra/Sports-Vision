from flask import Blueprint, render_template, request, flash, redirect, url_for
from core.db import get_db_connection
from services import admin_service
from services.ml_service import train_prediction_model

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin():
    """Admin panel main page."""
    conn = get_db_connection()
    
    players = conn.execute('SELECT * FROM players ORDER BY name').fetchall()
    matches = conn.execute('''
        SELECT m.*, 
               COUNT(mp.id) as player_count
        FROM matches m
        LEFT JOIN match_performance mp ON m.id = mp.match_id
        GROUP BY m.id
        ORDER BY m.match_date DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin.html', players=players, matches=matches)

@admin_bp.route('/admin/add_player', methods=['POST'])
def add_player_route():
    """Add a new player to the database."""
    name = request.form.get('name')
    position = request.form.get('position')
    jersey_number = request.form.get('jersey_number')
    age = request.form.get('age')
    nationality = request.form.get('nationality')
    
    admin_service.add_player(name, position, jersey_number, age, nationality)
    
    flash('Player added successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/add_match', methods=['POST'])
def add_match_route():
    """Add a new match to the database."""
    match_date = request.form.get('match_date')
    opponent = request.form.get('opponent')
    venue = request.form.get('venue')
    team_goals = int(request.form.get('team_goals', 0))
    opponent_goals = int(request.form.get('opponent_goals', 0))
    possession = float(request.form.get('possession', 50))
    shots = int(request.form.get('shots', 0))
    shots_on_target = int(request.form.get('shots_on_target', 0))
    corners = int(request.form.get('corners', 0))
    fouls = int(request.form.get('fouls', 0))
    
    admin_service.add_match(match_date, opponent, venue, team_goals, opponent_goals, possession, shots, shots_on_target, corners, fouls)
    
    flash('Match added successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/edit_player/<int:player_id>', methods=['POST'])
def edit_player_route(player_id):
    """Edit player information."""
    name = request.form.get('name')
    position = request.form.get('position')
    jersey_number = request.form.get('jersey_number')
    age = request.form.get('age')
    nationality = request.form.get('nationality')
    
    admin_service.edit_player(player_id, name, position, jersey_number, age, nationality)
    
    flash('Player updated successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/edit_stats/<int:player_id>', methods=['POST'])
def edit_player_stats_route(player_id):
    """Edit player statistics."""
    season = request.form.get('season')
    matches_played = int(request.form.get('matches_played', 0))
    goals = int(request.form.get('goals', 0))
    assists = int(request.form.get('assists', 0))
    passes_attempted = int(request.form.get('passes_attempted', 0))
    passes_completed = int(request.form.get('passes_completed', 0))
    minutes_played = int(request.form.get('minutes_played', 0))
    yellow_cards = int(request.form.get('yellow_cards', 0))
    red_cards = int(request.form.get('red_cards', 0))
    rating = float(request.form.get('rating', 0))
    
    admin_service.edit_player_stats(player_id, season, matches_played, goals, assists, passes_attempted, passes_completed, minutes_played, yellow_cards, red_cards, rating)
    
    flash('Player statistics updated successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/delete_player/<int:player_id>', methods=['POST'])
def delete_player_route(player_id):
    """Delete a player and all associated data."""
    admin_service.delete_player(player_id)
    flash('Player deleted successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/delete_match/<int:match_id>', methods=['POST'])
def delete_match_route(match_id):
    """Delete a match and all associated performance data."""
    admin_service.delete_match(match_id)
    flash('Match deleted successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/train_model', methods=['POST'])
def admin_train_model():
    """Train the ML model from admin panel."""
    model, message = train_prediction_model()
    
    if model:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('admin.admin'))
