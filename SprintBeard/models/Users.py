import binascii
from Model import check_uuid, cursor, db
import uuid
from uuid import UUID


class User:
	'''This class just holds data about a user, namely its name and uuid.'''
	def __init__(self, name, email, id):
		self.id = id
		self.name = name
		self.email = email
	
	def to_json(self):
		'''
		Convert to JSON
		'''
		attributes = self.__dict__
		return (
			'{"__class__": "User", "name": "%s", "email": "%s", "id": "%s"}' 
			% (attributes['name'], attributes['email'], attributes['id'])
		)

def user_from_json(dictionary):
	'''
	Convert from JSON
	'''
	return User(dictionary['name'], dictionary['email'], dictionary['id'])

def create(name, email):
	'''
	Add a new user to the database.
		arg: name - the name of the user to insert
		arg: email - the email of the user to insert

		return: the created User
	'''

	user = User(name, email, uuid.uuid4())

	cursor.execute('''
			INSERT INTO `users` (id, name, email)
			VALUES (%s, %s, %s)
		''',
		(user.id.bytes, user.name, user.email)
	)

	try:
		db.commit()
		return User(user.name, user.email, user.id.hex)
	except:
		db.rollback()

@check_uuid
def get(user_id):
	'''
	Select a user from the database by id
		arg: user_id - the id of the user to find

		return: an User object representing the found user or None if not found
	'''
	user_id = UUID(user_id)

	cursor.execute('''
			SELECT `id`, `name`, `email`
			FROM `users`
			WHERE `id`=%s
		''',
		(user_id.bytes)
	)

	user = None
	row = cursor.fetchone()
	if row is not None:
		user = User(row[1], row[2], binascii.b2a_hex(row[0]))
	return user

@check_uuid
def create_openid_association(userid, openid):
	'''
	Create an association between a user and an openid
		arg: userid - the id (as uuid) of the user for whom to create an association
		arg: openid - the openid to associate
	'''
	userid = UUID(userid)
	cursor.execute('''
			INSERT INTO `users_openids` (`user_id`, `openid`)
			VALUES(%s, %s)
		''',
		(userid.bytes, openid)
	)

	try:
		db.commit()
	except:
		db.rollback()

def get_by_openid(openid):
	'''
	Select a user from the database by openid
		arg: openid - the openid identifier of the user to find

		return: an User object representing the found user or None if not found
	'''

	cursor.execute('''
			SELECT `user_id`
			FROM `users_openids`
			WHERE `openid`=%s
		''',
		(openid)
	)

	user = None
	row = cursor.fetchone()
	if row is not None:
		user = get(binascii.b2a_hex(row[0]))
	return user

@check_uuid
def get_by_board(board_id):
	'''
	Get all the users that have access to a board.
		arg: board_id - the id of the board to get users for

		return: a List of User objects that have access to the board
	'''

	board_id = UUID(board_id)

	cursor.execute('''
		SELECT `name`, `email`, `id`
		FROM `users` INNER JOIN `users_boards`
		ON `users`.`id` = `users_boards`.`user_id`
		WHERE `board_id`=%s
		''',
		(board_id.bytes)
	)

	rows = cursor.fetchall()
	users = []
	for row in rows:
		users.append(User(row[0], row[1], binascii.b2a_hex(row[2])))
	return users

def update(id, name, email):
	'''
	Updates an existing user in the database.
		arg: id - the id of the user to be updated
		arg: name - the name of the user to be updated
		arg: email - the email of the user to updated
	'''

	cursor.execute('''
			UPDATE `users`
			SET `name`=%s,`email`=%s
			WHERE `id`=%s
		''',
		(name, email, UUID(id).bytes)
	)

	try:
		db.commit()
		return User(name, email, id)
	except:
		db.rollback()
