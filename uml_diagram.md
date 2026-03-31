```mermaid
classDiagram

    class Owner {
        int owner_id
        String name
        String email
        String phone_number
        int available_time
        List~String~ preferred_tasks
        List~Pet~ favorite_pets
        List~Pet~ current_pets
        add_current_pet(pet: Pet) void
        remove_current_pet(pet: Pet) void
        add_favorite_pet(pet: Pet) void
        remove_favorite_pet(pet: Pet) void
        change_email(new_email: String) void
    }

    class Pet {
        int pet_id
        String name
        int owner_id
        String species
        List~String~ dietary_preferences
        List~Task~ tasks
        change_owner(owner_id: int) void
    }

    class Task {
        int task_id
        String task_name
        boolean is_completed
        int duration
        int time
        enum priority HIGH, MEDIUM, LOW
        mark_complete() void
        edit_task(task_name: String, duration: int, time: int, priority: Priority) void
    }

    class Schedule {
        SortedList~Task~ schedule
        int total_time
        String explanation
        generate_schedule(tasks: List~Task~, available_time: int, preferred_tasks: List~String~) Schedule
        get_tasks() List~Task~
        get_explanation() String
    }

    Owner "1" --o "*" Pet : owns
    Owner "1" --o "1" Schedule : has
    Pet "1" --o "*" Task : has
    Schedule "1" --o "*" Task : contains
```
