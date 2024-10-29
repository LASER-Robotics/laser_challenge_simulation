import random
import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose, Point, Quaternion

# Lista das posições pré-definidas
bases_positions = [
    (6.5, -0.5, 0.05), (6.5, -1.5, 0.05), (6.5, -2.5, 0.05), (6.5, -3.5, 0.05), (6.5, -4.5, 0.05), (6.5, -5.5, 0.05),
    (5.5, 0.5, 0.05), (5.5, -0.5, 0.05), (5.5, -1.5, 0.05), (5.5, -2.5, 0.05), (5.5, -3.5, 0.05), (5.5, -4.5, 0.05), (5.5, -5.5, 0.05),
    (4.5, 0.5, 0.05), (4.5, -0.5, 0.05), (4.5, -1.5, 0.05), (4.5, -2.5, 0.05), (4.5, -3.5, 0.05), (4.5, -4.5, 0.05), (4.5, -5.5, 0.05),
    (3.5, -1.5, 0.05), (3.5, -2.5, 0.05), (3.5, -3.5, 0.05), (3.5, -4.5, 0.05), (3.5, -5.5, 0.05), 
    (2.5, -1.5, 0.05), (2.5, -2.5, 0.05), (2.5, -3.5, 0.05), (2.5, -4.5, 0.05), (2.5, -5.5, 0.05),
    (1.5, -1.5, 0.05), (1.5, -2.5, 0.05), (1.5, -3.5, 0.05), (1.5, -4.5, 0.05), (1.5, -5.5, 0.05),
    (0.5, -2.5, 0.05), (0.5, -3.5, 0.05), (0.5, -4.5, 0.05), 
    (0.0, -6.0, 1.5), (2.75, 0.0, 1.0)
]

def spawn(model_name, x, y, z, model_path):
    rospy.loginfo(f"Preparing to spawn model: {model_name} at ({x}, {y}, {z})")
    pose = Pose(Point(x, y, z), Quaternion(0, 0, 0, 1))
    try:
        with open(model_path, "r") as model_file:
            model_xml = model_file.read()
    except FileNotFoundError:
        rospy.logerr(f"Model file not found: {model_path}")
        return

    try:
        spawn_model_prox(model_name, model_xml, "", pose, "world")
        rospy.loginfo(f"Spawned {model_name} at position ({x}, {y}, {z})")
    except rospy.ServiceException as e:
        rospy.logerr(f"Failed to spawn model {model_name}: {e}")

def spawn_bases(bases_spawn):
    for idx in bases_spawn:
        rospy.loginfo(f"Spawning base at index: {idx}")
        model_name = f"base_{idx}"
        x, y, z = bases_positions[idx - 1]
        spawn(model_name, x, y, z, "/home/wagner/mrs_apptainer/user_ros_workspace/src/laser_challenge_simulation/models/landing_platform/model.sdf")

def spawn_qr_boxes(bases_spawn):
    qr_codes = ['a', 'b', 'c', 'd', 'e']  # Lista de QRCode
    random.shuffle(qr_codes)  # Embaralha os códigos

    # Spawn QR codes nas bases
    for idx in bases_spawn:
        if not qr_codes:
            rospy.logwarn("Não há mais QR Codes disponíveis para spawnear.")
            break
        code = qr_codes.pop()  # Remove e pega o último código da lista
        model_name = f"qrcode_box_{code}"
        x, y, z = bases_positions[idx - 1]
        z += 0.15  # Eleva a posição Z do QR Code
        model_path = f"/home/wagner/mrs_apptainer/user_ros_workspace/src/laser_challenge_simulation/models/qrcode_box_{code}/model.sdf"
        spawn(model_name, x, y, z, model_path)

if __name__ == "__main__":
    rospy.init_node("base_spawner")
    rospy.wait_for_service('/gazebo/spawn_sdf_model')
    spawn_model_prox = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)

    challenge_stage = rospy.get_param("~challenge_stage", "stage_one")
    bases_spawn_param = rospy.get_param("~bases_spawn", "")

    # Limpa a string e converte para lista de inteiros
    if bases_spawn_param:
        # Remove colchetes e divide a string em elementos
        bases_spawn_param = bases_spawn_param.strip('[]')  # Remove colchetes
        bases_spawn_param = bases_spawn_param.split(",")  # Divide em partes
        bases_spawn_param = [int(idx.strip()) for idx in bases_spawn_param if idx.strip()]  # Converte para inteiros

    if challenge_stage == "stage_one":
        if not bases_spawn_param:
            bases_spawn_param = random.sample(range(1, 38), 3)
        spawn_bases(bases_spawn_param)
    elif challenge_stage == "stage_two":
        rospy.loginfo("Fase 2: Não há spawns nesta fase.")
    elif challenge_stage == "stage_three":
        if not bases_spawn_param:
            bases_spawn_param = random.sample(range(1, 38), 3)
        spawn_bases(bases_spawn_param)        
        bases_spawn_param.append(39)
        bases_spawn_param.append(40)
        spawn_qr_boxes(bases_spawn_param)
    elif challenge_stage == "stage_four":
        bases_spawn_param = random.sample(range(1, 38), 4)
        spawn_bases(bases_spawn_param)