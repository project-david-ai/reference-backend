from entities import Entities

client = Entities()

user = client.users.create_user(name='test36')

#-----------------------------------------
#Creatres a vector store
#------------------------------------------

store = client.vectors.create_vector_store(
    name='default',
    user_id=user.id,

    )

#-----------------------------------------
# Upload a file to the vector store
#------------------------------------------

upload = client.vectors.add_file_to_vector_store(
    vector_store_id=store.id,
    file_path='movie_data.csv',

)

#-----------------------------------------
# Attaches store to an assistant
#-----------------------------------------
attach = client.vectors.attach_vector_store_to_assistant(
    vector_store_id=store.id,
    assistant_id='default'
)

print(store)