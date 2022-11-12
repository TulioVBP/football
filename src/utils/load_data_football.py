from FootballDataset import FootballDataset
from torch.utils import data

# TODO - bring this function inside the train_model function

# Data loading


def load_data_football(
    batch_size, num_par, cat_par, target, input_path, to_predict=False
):  # @save
    """Load the dataset into memory."""
    # Load dataset
    dataset = FootballDataset(
        cat_par, num_par, target, csv_file=input_path
    )  # ,league = ["La liga"], season = [2015,2016] )

    if not to_predict:
        # Split into training and test
        train_size = int(0.8 * len(dataset))
        test_size = len(dataset) - train_size
        trainset, testset = data.random_split(dataset, [train_size, test_size])

        # Dataloaders
        return (
            data.DataLoader(trainset, batch_size=batch_size, shuffle=True),
            data.DataLoader(testset, batch_size=batch_size, shuffle=False),
        )
    else:
        # Return the full list
        return data.DataLoader(dataset, shuffle=False)
