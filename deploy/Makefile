check-env:
ifndef AWS_PROFILE
	$(error AWS_PROFILE is undefined, Use export AWS_PROFILE=your_profile to export the profile)
endif

cdk-synth: check-env
	cdk synth --all

cdk-deploy: cdk-synth
	cdk deploy --all